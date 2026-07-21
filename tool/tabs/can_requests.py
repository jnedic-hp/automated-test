# @file    can_requests.py
# @brief   CAN Requests panel - send requests from HMI/OMS to CB, display responses.

import dataclasses
import tkinter as tk
import can
from tkinter import ttk
from datetime import datetime
from typing import Callable, Optional

from common_cfg import Common
from common.can_interface import CanMessage
from common.can_protocol import (L0_HMI_COB, L0_CB_COB, L1_OMS_COB, L1_CB_COB,
                                 L0_HMI_RequestMessages, L0_HMI_CommandMessages,
                                 L1_OMS_NotificationMessages, L1_OMS_PeriodicMessages, L1_OMS_ResponseMessages,
                                 L1_OMS_DataMessages,
                                 L0_CB_NotificationMessages, L0_CB_ResponseMessages,
                                 BoardVersionResponse,)

# Alias
STATE = Common.State
TAG = Common.Tag


_L0_MSG = [
    ("Request Board Version",               L0_HMI_RequestMessages.RequestBoardVersion),
    ("Request UI Ready",                    L0_HMI_RequestMessages.RequestUiReady),
    ("Request Preheat Start",               L0_HMI_RequestMessages.RequestPreheatStart),
    ("Request Preheat Stop",                L0_HMI_RequestMessages.RequestPreheatStop),
    ("Request Cook Timer Start",            L0_HMI_RequestMessages.RequestCookTimerStart),
    ("Request Cook Timer Stop",             L0_HMI_RequestMessages.RequestCookTimerStop),
    ("Request Cook Timer Complete",         L0_HMI_RequestMessages.RequestCookTimerComplete),
    ("Request Vat On/Off",                  L0_HMI_CommandMessages.CommandVatOnOff),
    ("Request Eco Mode",                    L0_HMI_RequestMessages.RequestEcoMode),
    ("Request Rapid Heat",                  L0_HMI_RequestMessages.RequestRapidHeat),
    ("Request Fryer Shutdown",              L0_HMI_RequestMessages.RequestFryerShutdown),
    ("Request Filter Pause",                L0_HMI_RequestMessages.RequestFilterPause),
    ("Request Filter Resume",               L0_HMI_RequestMessages.RequestFilterResume),
    ("Request Filter Skip Step",            L0_HMI_RequestMessages.RequestFilterSkipStep),
    ("Request Filter Stop",                 L0_HMI_RequestMessages.RequestFilterStop),
    ("Request Filter Dialog Response",      L0_HMI_RequestMessages.RequestFilterDialogResponse),
    ("Request Express Filter Later",        L0_HMI_RequestMessages.RequestExpressFilterLater),
    ("Request Express Filter Ready",        L0_HMI_RequestMessages.RequestExpressFilterReady),
    ("Request Express Filter Start",        L0_HMI_RequestMessages.RequestExpressFilterStart),
    ("Request Daily Filter Later",          L0_HMI_RequestMessages.RequestDailyFilterLater),
    ("Request Daily Filter Ready",          L0_HMI_RequestMessages.RequestDailyFilterReady),
    ("Request Daily Filter Start",          L0_HMI_RequestMessages.RequestDailyFilterStart),
    ("Request Fill Set Source",             L0_HMI_RequestMessages.RequestFillSetSource),
    ("Request Fill Start",                  L0_HMI_RequestMessages.RequestFillStart),
    ("Request Fill Stop",                   L0_HMI_RequestMessages.RequestFillStop),
    ("Request Drain To Pan Start",          L0_HMI_RequestMessages.RequestDrainToPanStart),
    ("Request Drain To Pan Stop",           L0_HMI_RequestMessages.RequestDrainToPanStop),
    ("Request Dispose Start",               L0_HMI_RequestMessages.RequestDisposeStart),
    ("Request Dispose Stop",                L0_HMI_RequestMessages.RequestDisposeStop),
    ("Request Oil Mgmt Task Start",         L0_HMI_RequestMessages.RequestOilMgmtTaskStart),
    ("Request Oil Mgmt Task End",           L0_HMI_RequestMessages.RequestOilMgmtTaskEnd),
    ("Request Clear Error",                 L0_HMI_RequestMessages.RequestClearError),
    ("Request Product Names Request",       L0_HMI_RequestMessages.RequestProductNamesRequest),
    ("Request Product Data Request",        L0_HMI_RequestMessages.RequestProductDataRequest),
    ("Request Update Settings",             L0_HMI_RequestMessages.RequestUpdateSettings),
    ("Request Well Wizard Start",           L0_HMI_RequestMessages.RequestWellWizardStart),
    ("Request Well Wizard Set",             L0_HMI_RequestMessages.RequestWellWizardSet),
    ("Request HMI Board Version Info",      L0_HMI_RequestMessages.RequestHmiBoardVersionInfo),
]

_L1_MSG = [
    ("Response Selector Valve",             L1_OMS_ResponseMessages.ResponseSelectorValve),
    ("Response Drain Valve",                L1_OMS_ResponseMessages.ResponseDrainValve),
    ("Response Filter Pump",                L1_OMS_ResponseMessages.ResponseFilterPump),
    ("Response Token Grant",                L1_OMS_ResponseMessages.ResponseTokenGrant),
    ("Response Token Release Ack",          L1_OMS_ResponseMessages.ResponseTokenReleaseAck),
    ("Notification Dispose Switch State",   L1_OMS_NotificationMessages.NotificationDisposeSwitchState),
    ("Notification USB State",              L1_OMS_NotificationMessages.NotificationUsbState),
    ("Response OMS Version",                L1_OMS_ResponseMessages.ResponseOmsVersion),
    ("Notification OMS Bulk",               L1_OMS_NotificationMessages.NotificationOmsBulk),
    ("Data Bulk Transfer Buffer",           L1_OMS_DataMessages.DataBulkTransferBuffer),
    ("OMS Board Status",                    L1_OMS_PeriodicMessages.PeriodicOmsBoardStatus),
    ("Response Well Wizard Start",          L1_OMS_ResponseMessages.ResponseOmsWellWizardStart),
    ("Notification Well Wizard Status",     L1_OMS_NotificationMessages.NotificationOmsWellWizardStatus),
    ("Notification Bulk Tank Full",         L1_OMS_NotificationMessages.NotificationBulkTankFull),
    ("Notification Bulk 24VAC Input",       L1_OMS_NotificationMessages.NotificationBulk24VacInput),
    ("Serial Number Ack Response",          L1_OMS_ResponseMessages.ResponseSerialNumberAck),
    ("Notification Filter Pump Dead Head",  L1_OMS_NotificationMessages.NotificationFilterPumpDeadHead),
]

# COB-ID → name reverse lookup (for response labels)
_COB_NAME: dict[int, str] = {}
for _cob_cls in (L0_CB_COB, L1_CB_COB, L0_HMI_COB, L1_OMS_COB):
    for _attr, _val in vars(_cob_cls).items():
        if isinstance(_val, type):  # nested sub-class (Response, Notification, Periodic, etc.)
            for _sub_attr, _sub_val in vars(_val).items():
                if not _sub_attr.startswith("_") and isinstance(_sub_val, int):
                    _COB_NAME[_sub_val] = _sub_attr
        elif not _attr.startswith("_") and isinstance(_val, int):
            _COB_NAME[_val] = _attr

# Request - Response Mapping
_L0_RESP_MAP: dict = {
    L0_HMI_RequestMessages.RequestBoardVersion:        (BoardVersionResponse,                                            L0_CB_COB.ResponseMessage.RSP_BOARD_VERSION),
    L0_HMI_RequestMessages.RequestUiReady:             (L0_CB_ResponseMessages.ResponseBackendReady,                     L0_CB_COB.ResponseMessage.RSP_BACKEND_READY),
    L0_HMI_RequestMessages.RequestPreheatStart:        (L0_CB_NotificationMessages.NotificationPreheatStarted,           L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_START),
    L0_HMI_RequestMessages.RequestPreheatStop:         (L0_CB_NotificationMessages.NotificationPreheatStopped,           L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_STOP),
    L0_HMI_RequestMessages.RequestCookTimerStart:      (L0_CB_NotificationMessages.NotificationCookTimerStarted,         L0_CB_COB.NotificationMessage.NOTIFY_COOK_START),
    L0_HMI_RequestMessages.RequestCookTimerStop:       (L0_CB_NotificationMessages.NotificationCookTimerStopped,         L0_CB_COB.NotificationMessage.NOTIFY_COOK_STOP),
    L0_HMI_RequestMessages.RequestEcoMode:             (L0_CB_NotificationMessages.NotificationEcoMode,                  L0_CB_COB.NotificationMessage.NOTIFY_ECO_MODE),
    L0_HMI_RequestMessages.RequestRapidHeat:           (L0_CB_NotificationMessages.NotificationRapidHeat,                L0_CB_COB.NotificationMessage.NOTIFY_RAPID_HEAT),
    L0_HMI_RequestMessages.RequestFryerShutdown:       (L0_CB_NotificationMessages.NotificationShutdown,                 L0_CB_COB.NotificationMessage.NOTIFY_SHUTDOWN),
    L0_HMI_RequestMessages.RequestFilterPause:         (L0_CB_NotificationMessages.NotificationFilterPause,              L0_CB_COB.NotificationMessage.NOTIFY_FILTER_PAUSE),
    L0_HMI_RequestMessages.RequestFilterResume:        (L0_CB_NotificationMessages.NotificationFilterResume,             L0_CB_COB.NotificationMessage.NOTIFY_FILTER_RESUME),
    L0_HMI_RequestMessages.RequestFilterSkipStep:      (L0_CB_NotificationMessages.NotificationFilterSkipStep,           L0_CB_COB.NotificationMessage.NOTIFY_FILTER_SKIP_STEP),
    L0_HMI_RequestMessages.RequestFilterStop:          (L0_CB_NotificationMessages.NotificationFilterStop,               L0_CB_COB.NotificationMessage.NOTIFY_FILTER_STOP),
    L0_HMI_RequestMessages.RequestExpressFilterLater:  (L0_CB_NotificationMessages.NotificationExpressFilterLater,       L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_LATER),
    L0_HMI_RequestMessages.RequestExpressFilterReady:  (L0_CB_NotificationMessages.NotificationExpressFilterReady,       L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_READY),
    L0_HMI_RequestMessages.RequestExpressFilterStart:  (L0_CB_NotificationMessages.NotificationExpressFilterStarted,     L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_STARTED),
    L0_HMI_RequestMessages.RequestDailyFilterLater:    (L0_CB_NotificationMessages.NotificationDailyFilterLater,         L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_LATER),
    L0_HMI_RequestMessages.RequestDailyFilterReady:    (L0_CB_NotificationMessages.NotificationDailyFilterReady,         L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_READY),
    L0_HMI_RequestMessages.RequestDailyFilterStart:    (L0_CB_NotificationMessages.NotificationDailyFilterStarted,       L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_STARTED),
    L0_HMI_RequestMessages.RequestOilMgmtTaskStart:    (L0_CB_NotificationMessages.NotificationOilMgmtTaskStart,         L0_CB_COB.NotificationMessage.NOTIFY_OIL_MGMT_TASK_START),
    L0_HMI_RequestMessages.RequestOilMgmtTaskEnd:      (L0_CB_NotificationMessages.NotificationOilMgmtTaskEnd,           L0_CB_COB.NotificationMessage.NOTIFY_OIL_MGMT_TASK_END),
    L0_HMI_RequestMessages.RequestUpdateSettings:      (L0_CB_NotificationMessages.NotificationHpunitSettings,           L0_CB_COB.NotificationMessage.NOTIFY_HPUNIT_SETTINGS),
    L0_HMI_RequestMessages.RequestWellWizardStart:     (L0_CB_NotificationMessages.NotificationStartWellWizard,          L0_CB_COB.NotificationMessage.NOTIFY_START_WELL_WIZARD),
    L0_HMI_RequestMessages.RequestWellWizardSet:       (L0_CB_NotificationMessages.NotificationWellWizardStatus,         L0_CB_COB.NotificationMessage.NOTIFY_WELL_WIZARD_STATUS),
}


class CanRequests:
    TEXT_CAN_LINE  = "CAN Line:"
    TEXT_MSG       = "Message:"
    TEXT_PARAMS    = "Message Parameters"
    TEXT_REQ       = "Request Message Data"
    TEXT_RSP       = "Response Message Data"
    TEXT_SEND      = "Send"
    TEXT_CLEAR     = "Clear"
    TEXT_NO_PARAMS = "No Parameters"
    TEXT_RESPONSE  = "No Response"


    def __init__(self, parent: ttk.Frame, bus_getter: Callable,
                 log_fn: Callable, register_rx: Callable,
                 register_rx_all: Optional[Callable] = None, **_kwargs,) -> None:
        self._bus_getter = bus_getter
        self._log = log_fn
        self._field_vars: dict[str, tk.StringVar] = {}
        self._current_cls = None
        self._rsp_cob_id: Optional[int] = None
        self._rsp_cls = None
        self._rsp_field_vars: dict[str, tk.StringVar] = {}
        self._rsp_header_var: Optional[tk.StringVar] = None

        self._build_ui(parent)
        self._on_line_changed()

        if register_rx_all:
            register_rx_all(self._on_rx)


    def _build_ui(self, parent: ttk.Frame) -> None:
        can_line_values = ["Line 0: HMI → CB",
                           "Line 1: OMS → CB",]

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        parent.rowconfigure(2, weight=2)

        # CAN Line
        can_frame = ttk.Frame(parent)
        can_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=4)
        can_frame.columnconfigure(1, weight=1)

        text_can_line_label = ttk.Label(can_frame, text=self.TEXT_CAN_LINE)
        text_can_line_label.grid(row=0, column=0, sticky="w", padx=(0, 4))

        self._can_line_var = tk.StringVar(value=can_line_values[0])

        self._can_line_combobox = ttk.Combobox(can_frame,
                                               textvariable=self._can_line_var,
                                               values=can_line_values,
                                               state=STATE.RO,)
        self._can_line_combobox.grid(row=0, column=1, sticky="ew")
        self._can_line_combobox.bind("<<ComboboxSelected>>",
                                     lambda _: self._on_line_changed(),)

        # Request Message Data
        req_frame = ttk.LabelFrame(parent, text=self.TEXT_REQ, padding=6,)
        req_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=4,)
        req_frame.columnconfigure(0, weight=0)
        req_frame.columnconfigure(1, weight=1)
        req_frame.columnconfigure(2, weight=0)
        req_frame.columnconfigure(3, weight=0)
        req_frame.columnconfigure(4, weight=0)
        req_frame.rowconfigure(2, weight=1)

        text_msg_label = ttk.Label(req_frame, text=self.TEXT_MSG)
        text_msg_label.grid(row=0, column=0, sticky="w", padx=(0, 4),)

        self._msg_option = tk.StringVar()

        self._msg_combobox = ttk.Combobox(req_frame, textvariable=self._msg_option, state=STATE.RO,)
        self._msg_combobox.grid(row=0, column=1, sticky="ew", pady=(0, 6),)
        self._msg_combobox.bind("<<ComboboxSelected>>",
                                lambda _: self._on_msg_changed(),)
        
        text_params_label = ttk.Label(req_frame, text=self.TEXT_PARAMS)
        text_params_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 2),)

        self._params_canvas = tk.Canvas(req_frame, height=100, highlightthickness=0,)

        params_scroll = ttk.Scrollbar(req_frame, orient="vertical", command=self._params_canvas.yview,)

        self._params_frame = ttk.Frame(self._params_canvas)
        self._params_frame.bind("<Configure>",
                                lambda e: self._params_canvas.configure(scrollregion=self._params_canvas.bbox("all")),)

        self._params_canvas.create_window((0, 0), window=self._params_frame, anchor="nw",)
        self._params_canvas.configure(yscrollcommand=params_scroll.set)
        self._params_canvas.grid(row=2, column=0, columnspan=2, sticky="nsew",)
        params_scroll.grid(row=2, column=2, sticky="ns",)
        
        req_separator = ttk.Separator(req_frame, orient="vertical")
        req_separator.grid(row=0, column=3, rowspan=3, sticky="ns", padx=(8, 8),)
        
        self._send_btn = ttk.Button(req_frame, text=self.TEXT_SEND, width=12, command=self._send,)
        self._send_btn.grid(row=0, column=4, rowspan=3, padx=8, sticky="",)

        # Response Message Data
        rsp_frame = ttk.LabelFrame(parent, text=self.TEXT_RSP, padding=6,)
        rsp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=4, pady=(0, 4),)

        self._rsp_data_canvas = tk.Canvas(rsp_frame, height=150, highlightthickness=0,)

        rsp_scroll = ttk.Scrollbar(rsp_frame, orient="vertical", command=self._rsp_data_canvas.yview,)

        self._rsp_data_frame = ttk.Frame(self._rsp_data_canvas)
        self._rsp_data_frame.bind("<Configure>",
                                  lambda e: self._rsp_data_canvas.configure(scrollregion=self._rsp_data_canvas.bbox("all")),)

        self._rsp_data_win_id = self._rsp_data_canvas.create_window((0, 0), window=self._rsp_data_frame, anchor="nw",)

        self._rsp_data_canvas.bind("<Configure>",
                                   lambda e: self._rsp_data_canvas.itemconfigure(self._rsp_data_win_id, width=e.width,),)
        self._rsp_data_canvas.configure(yscrollcommand=rsp_scroll.set)

        rsp_frame.columnconfigure(0, weight=1)
        rsp_frame.columnconfigure(1, weight=0)  # scrollbar
        rsp_frame.columnconfigure(2, weight=0)  # vertical separator
        rsp_frame.columnconfigure(3, weight=0)  # clear button
        rsp_frame.rowconfigure(0, weight=1)

        self._rsp_data_canvas.grid(row=0, column=0, sticky="nsew",)

        rsp_scroll.grid(row=0, column=1, sticky="ns",)

        rsp_separator = ttk.Separator(rsp_frame, orient="vertical")
        rsp_separator.grid(row=0, column=2, sticky="ns", padx=(8, 8),)

        clear_button = ttk.Button(rsp_frame, text=self.TEXT_CLEAR, width=12, command=self._clear_responses)
        clear_button.grid(row=0, column=3, padx=8, sticky="",)


    # Event handlers
    def _on_line_changed(self) -> None:
        message_list = _L0_MSG if self._can_line_combobox.current() == 0 else _L1_MSG
        names = [name for name, _ in message_list]
        self._msg_combobox.configure(values=names)
        if names:
            self._msg_combobox.current(0)
        self._on_msg_changed()

    def _on_msg_changed(self) -> None:
        message_list = _L0_MSG if self._can_line_combobox.current() == 0 else _L1_MSG
        name = self._msg_option.get()
        cls = next((c for n, c in message_list if n == name), None)
        self._current_cls = cls
        self._rebuild_params(cls)
        self._rebuild_rsp(cls)

    def _rebuild_params(self, cls) -> None:
        for widget in self._params_frame.winfo_children():
            widget.destroy()
        self._field_vars.clear()

        no_fields = (cls is None
                     or not dataclasses.is_dataclass(cls)
                     or not dataclasses.fields(cls))
        if no_fields:
            params_frame_label = ttk.Label(self._params_frame, text=self.TEXT_NO_PARAMS, foreground="#888888")
            params_frame_label.grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
            return

        for i, field in enumerate(dataclasses.fields(cls)):
            default = field.default if field.default is not dataclasses.MISSING else 0

            params_frame_label = ttk.Label(self._params_frame, text=f"{field.name}:")
            params_frame_label.grid(row=i, column=0, sticky=tk.W, padx=(4, 8), pady=2,)

            var = tk.StringVar(value=str(default))
            self._field_vars[field.name] = var

            params_frame_entry = ttk.Entry(self._params_frame, textvariable=var, width=10)
            params_frame_entry.grid(row=i, column=1, sticky=tk.W, pady=2)


    def _rebuild_rsp(self, request_cls) -> None:
        for w in self._rsp_data_frame.winfo_children():
            w.destroy()
        self._rsp_field_vars.clear()
        self._rsp_cob_id = None
        self._rsp_cls = None
        self._rsp_header_var = None

        if self._can_line_combobox.current() != 0:
            return

        entry = _L0_RESP_MAP.get(request_cls)
        if entry is None:
            rsp_data_frame_label = ttk.Label(self._rsp_data_frame, text=self.TEXT_RESPONSE, foreground="#888888")
            rsp_data_frame_label.grid(row=0, column=0, sticky="w", padx=4, pady=4)
            return

        resp_cls, resp_cob_id = entry
        self._rsp_cls = resp_cls
        self._rsp_cob_id = resp_cob_id
        rsp_name = _COB_NAME.get(resp_cob_id, f"0x{resp_cob_id:04X}")
        self._rsp_header_var = tk.StringVar(value=f"Response Msg:  {rsp_name}  (0x{resp_cob_id:04X})")

        rsp_data_frame_label = ttk.Label(self._rsp_data_frame, textvariable=self._rsp_header_var)
        rsp_data_frame_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=(4, 4), pady=(4, 2))

        if dataclasses.is_dataclass(resp_cls) and dataclasses.fields(resp_cls):
            for i, field in enumerate(dataclasses.fields(resp_cls), start=1):
                rsp_data_frame_label = ttk.Label(self._rsp_data_frame, text=f"{field.name}:")
                rsp_data_frame_label.grid(row=i, column=0, sticky="w", padx=(4, 8), pady=2,)
                var = tk.StringVar(value="---")
                rsp_data_entry = ttk.Entry(self._rsp_data_frame, textvariable=var, state=STATE.RO, width=10)
                rsp_data_entry.grid(row=i, column=1, sticky="w", pady=2)
                self._rsp_field_vars[field.name] = var
        else:
            rsp_data_frame_label = ttk.Label(self._rsp_data_frame, text=self.TEXT_NO_PARAMS, foreground="#888888")
            rsp_data_frame_label.grid(row=1, column=0, sticky="w", padx=4)


    # CAN Communications
    def _send(self) -> None:
        bus = self._bus_getter()
        if bus is None:
            self._log("Not Connected - Connect USB to CAN Adapter first.", tag=TAG.ERR)
            return

        cls = self._current_cls
        if cls is None:
            return
        
        try:
            if dataclasses.is_dataclass(cls) and dataclasses.fields(cls):
                kwargs = {f.name: int(self._field_vars[f.name].get(), 0)
                          for f in dataclasses.fields(cls)}
                msg = cls(**kwargs).encode()
            else:
                msg = cls().encode()
        except Exception as exc:
            self._log(f"Encode error: {exc}", tag=TAG.ERR)
            return

        raw = can.Message(arbitration_id=msg.arbitration_id,
                          data=msg.data,
                          is_extended_id=False,)
        try:
            bus.send(raw)
        except Exception as exc:
            self._log(f"TX error: {exc}", tag=TAG.ERR)
            return

        name = _COB_NAME.get(msg.arbitration_id, "UNKNOWN")
        self._log(f"TX  0x{msg.arbitration_id:04X}  {name}  data={bytes(msg.data).hex()}",
                  tag="tx",)

    def _on_rx(self, raw: can.Message) -> None:
        name = _COB_NAME.get(raw.arbitration_id, "UNKNOWN")
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Decode and update response data display when COB-ID matches
        if self._rsp_cob_id is not None and raw.arbitration_id == self._rsp_cob_id:
            try:
                _cm = CanMessage(arbitration_id=raw.arbitration_id, data=bytes(raw.data))
                decoded = self._rsp_cls.from_can(_cm)
                if dataclasses.is_dataclass(decoded):
                    for field in dataclasses.fields(decoded):
                        if field.name in self._rsp_field_vars:
                            self._rsp_field_vars[field.name].set(str(getattr(decoded, field.name)))
                if self._rsp_header_var is not None:
                    resp_cob_name = _COB_NAME.get(raw.arbitration_id, f"0x{raw.arbitration_id:04X}")
                    self._rsp_header_var.set(f"Response:  {resp_cob_name}  (0x{raw.arbitration_id:04X})  [{ts}]")
            except Exception:
                pass

        line = f"[{ts}]  0x{raw.arbitration_id:04X}  {name}  {bytes(raw.data).hex()}\n"
        self._log(line.rstrip(), tag="rx")

    def _clear_responses(self) -> None:
        for var in self._rsp_field_vars.values():
            var.set("---")
        if self._rsp_header_var is not None and self._rsp_cob_id is not None:
            rsp_name = _COB_NAME.get(self._rsp_cob_id, f"0x{self._rsp_cob_id:04X}")
            self._rsp_header_var.set(f"Response Msg:  {rsp_name}  (0x{self._rsp_cob_id:04X})")
