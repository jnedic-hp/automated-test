# @file    can_protocol.py
# @brief   CAN protocol definitions and message encoders/decoders.
# @details Defines COB-IDs, dataclass message types, and encode/decode
#          helpers for the L0 CAN line (CB <-> HMI).

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import ClassVar

from common.can_interface import CanMessage


# ===========================================================================
# Line 0 (FDCAN1) COB-ID constants (CB <-> HMI)
# ===========================================================================
class L0_HMI_COB:
    class RequestMessage:
        REQ_BOARD_VERSION               = 0x143a  # RPDO57 - L0_I_REQUEST_BOARD_VERSION_INFO
        REQ_UI_READY                    = 0x1429  # RPDO26 - L0_I_REQUEST_UI_READY1
        REQ_BOARD_VERSION_INFO          = 0x1437  # RPDO56 - L0_I_HMI_BOARD_VERSION_INFO
        REQ_PREHEAT_START               = 0x1408  # RPDO25 - L0_I_REQUEST_PREHEAT_START
        REQ_PREHEAT_STOP                = 0x1409  # RPDO26 - L0_I_REQUEST_PREHEAT_STOP
        REQ_COOK_TIMER_START            = 0x1401  # RPDO2  - L0_I_REQUEST_COOK_TIMER_START
        REQ_COOK_TIMER_STOP             = 0x1402  # RPDO3  - L0_I_REQUEST_COOK_TIMER_STOP
        REQ_COOK_TIMER_COMPLETE         = 0x1406  # RPDO7  - L0_I_REQUEST_COOK_TIMER_COMPLETE
        REQ_ECO_MODE                    = 0x140a  # RPDO11 - L0_I_REQUEST_ECO_MODE
        REQ_RAPID_HEAT                  = 0x140b  # RPDO12 - L0_I_REQUEST_RAPID_HEAT
        REQ_UPDATE_SETTINGS             = 0x142a  # RPDO27 - L0_I_REQUEST_UPDATE_SETTINGS
        REQ_FRYER_SHUTDOWN              = 0x1405  # RPDO6  - L0_I_RECEIVE_PDO_REQUEST_FRYER_SHUTDOWN
        REQ_FILTER_PAUSE                = 0x140e  # RPDO15 - L0_I_REQUEST_FILTER_PAUSE
        REQ_FILTER_RESUME               = 0x140f  # RPDO16 - L0_I_REQUEST_FILTER_RESUME
        REQ_FILTER_SKIP_STEP            = 0x1410  # RPDO17 - L0_I_REQUEST_FILTER_SKIP_STEP
        REQ_FILTER_STOP                 = 0x1413  # RPDO20 - L0_I_REQUEST_FILTER_STOP
        REQ_FILTER_DIALOG_RESPONSE      = 0x1428  # RPDO41 - L0_I_REQUEST_FILTER_DIALOG_RESPONSE
        REQ_EXPRESS_FILTER_LATER        = 0x1414  #        - L0_I_REQUEST_EXPRESS_FILTER_LATER
        REQ_EXPRESS_FILTER_READY        = 0x1415  #        - L0_I_REQUEST_EXPRESS_FILTER_READY
        REQ_EXPRESS_FILTER_START        = 0x1416  #        - L0_I_REQUEST_EXPRESS_FILTER_START
        REQ_DAILY_FILTER_LATER          = 0x1417  #        - L0_I_REQUEST_DAILY_FILTER_LATER
        REQ_DAILY_FILTER_READY          = 0x1418  #        - L0_I_REQUEST_DAILY_FILTER_READY
        REQ_DAILY_FILTER_START          = 0x1446  #        - L0_I_REQUEST_DAILY_FILTER_START
        REQ_FILL_SET_SOURCE             = 0x1419  #        - L0_I_REQUEST_FILL_SET_SOURCE
        REQ_FILL_START                  = 0x141a  #        - L0_I_REQUEST_FILL_START
        REQ_FILL_STOP                   = 0x141b  #        - L0_I_REQUEST_FILL_STOP
        REQ_DRAIN_TO_PAN_START          = 0x1420  #        - L0_I_REQUEST_DRAIN_TO_PAN_START
        REQ_DRAIN_TO_PAN_STOP           = 0x1421  #        - L0_I_REQUEST_DRAIN_TO_PAN_STOP
        REQ_DISPOSE_START               = 0x1423  #        - L0_I_REQUEST_DISPOSE_START
        REQ_DISPOSE_STOP                = 0x1424  #        - L0_I_REQUEST_DISPOSE_STOP
        REQ_OIL_MGMT_TASK_START         = 0x142b  # RPDO29 - L0_I_REQUEST_START_OIL_MANAGEMENT_TASK
        REQ_OIL_MGMT_TASK_END           = 0x1434  # RPDO55 - L0_I_REQUEST_END_OIL_MANAGEMENT_TASK
        REQ_CLEAR_ERROR                 = 0x1440  # RPDO65 - L0_I_REQUEST_CLEAR_ERROR
        REQ_PRODUCT_NAMES               = 0x142d  #        - L0_I_REQUEST_PRODUCT_NAMES
        REQ_PRODUCT_DATA                = 0x142e  #        - L0_I_REQUEST_PRODUCT_DATA
        REQ_START_WELL_WIZARD           = 0x1444  # RPDO69 - L0_I_REQUEST_START_WELL_WIZARD
        REQ_WELL_WIZARD_SET             = 0x1445  # RPDO70 - L0_I_REQUEST_WELL_WIZARD_SET
    class CommandMessage:
        CMD_VAT_ON_OFF                  = 0x2062  #        - L0_I_CMDVATONOFF

class L0_CB_COB:
    class ResponseMessage:
        RSP_BOARD_VERSION               = 0x1830  # TPDO49 - L0_I_RECEIVED_BOARD_VERSION_INFO
        RSP_BACKEND_READY               = 0x1829  # TPDO42 - L0_I_BACKEND_READY
    class NotificationMessage:
        NOTIFY_FRYER_STARTUP            = 0x180c  #        - L0_I_TRANSMIT_PDO_NOTIFY_FRYER_STARTUP
        NOTIFY_SHUTDOWN                 = 0x180b  # TPDO14 - L0_I_NOTIFY_SHUTDOWN
        NOTIFY_PREHEAT_START            = 0x1807  # TPDO10 - L0_I_NOTIFY_PREHEAT_START
        NOTIFY_PREHEAT_STOP             = 0x180a  # TPDO13 - L0_I_NOTIFY_PREHEAT_STOP
        NOTIFY_PREHEAT_UPDATE           = 0x1808  # TPDO11 - L0_I_NOTIFY_PREHEAT_UPDATE
        NOTIFY_PREHEAT_COMPLETE         = 0x1809  # TPDO12 - L0_I_NOTIFY_PREHEAT_COMPLETE
        NOTIFY_COOK_START               = 0x1803  # TPDO4  - L0_I_NOTIFY_COOK_TIMER_START_RECIEVED
        NOTIFY_COOK_STOP                = 0x1804  # TPDO5  - L0_I_NOTIFY_COOK_TIMER_STOP
        NOTIFY_COOK_UPDATE              = 0x1805  # TPDO6  - L0_I_NOTIFY_COOK_TIMER_UPDATE
        NOTIFY_ECO_MODE                 = 0x180e  # TPDO17 - L0_I_NOTIFY_ECO_MODE
        NOTIFY_RAPID_HEAT               = 0x180f  # TPDO18 - L0_I_NOTIFY_RAPID_HEAT
        NOTIFY_HPUNIT_SETTINGS          = 0x182a  # TPDO43 - L0_I_NOTIFY_HPUNIT_SETTINGS
        NOTIFY_FILTER_PAUSE             = 0x1811  #        - L0_I_NOTIFY_FILTER_PAUSE
        NOTIFY_FILTER_RESUME            = 0x1812  #        - L0_I_NOTIFY_FILTER_RESUME
        NOTIFY_FILTER_SKIP_STEP         = 0x1813  # TPDO26 - L0_I_NOTIFY_FILTER_SKIP_STEP
        NOTIFY_FILTER_FINISHED          = 0x1816  #        - L0_I_NOTIFY_FILTER_FINISHED
        NOTIFY_FILTER_STOP              = 0x1817  #        - L0_I_NOTIFY_FILTER_STOP
        NOTIFY_EXPRESS_FILTER_ALERT     = 0x1818  #        - L0_I_NOTIFY_EXPRESS_FILTER_ALERT
        NOTIFY_EXPRESS_FILTER_LATER     = 0x1819  #        - L0_I_NOTIFY_EXPRESS_FILTER_LATER
        NOTIFY_EXPRESS_FILTER_READY     = 0x181a  #        - L0_I_NOTIFY_EXPRESS_FILTER_READY
        NOTIFY_EXPRESS_FILTER_STARTED   = 0x181b  #        - L0_I_NOTIFY_EXPRESS_FILTER_STARTED_VAT
        NOTIFY_EXPRESS_FILTER_STEP      = 0x181c  #        - L0_I_NOTIFY_EXPRESS_FILTER_STEP
        NOTIFY_DAILY_FILTER_ALERT       = 0x181d  #        - L0_I_NOTIFY_DAILY_FILTER_ALERT
        NOTIFY_DAILY_FILTER_LATER       = 0x181e  #        - L0_I_NOTIFY_DAILY_FILTER_LATER
        NOTIFY_DAILY_FILTER_READY       = 0x181f  #        - L0_I_NOTIFY_DAILY_FILTER_READY
        NOTIFY_DAILY_FILTER_STARTED     = 0x1820  #        - L0_I_NOTIFY_DAILY_FILTER_STARTED
        NOTIFY_DAILY_FILTER_STEP_UPDATE = 0x1821  #        - L0_I_NOTIFY_DAILY_FILTER_STEP_UPDATE
        NOTIFY_VALVE_STATE              = 0x1827  #        - L0_I_NOTIFY_VALVE_STATE
        NOTIFY_OIL_MGMT_TASK_START      = 0x1823  #        - L0_I_NOTIFY_START_OIL_MANAGEMENT_TASK
        NOTIFY_OIL_MGMT_TASK_END        = 0x1824  #        - L0_I_NOTIFY_END_OIL_MANAGEMENT_TASK
        NOTIFY_OIL_MGMT_STEP            = 0x182b  #        - L0_I_NOTIFY_OIL_MANAGEMENT_STEP
        NOTIFY_REAR_DISPOSE_COUNTDOWN   = 0x182c  #        - L0_I_NOTIFY_REAR_DISPOSE_COUNTDOWN
        NOTIFY_SHAKE_ALERT              = 0x182d  #        - L0_I_NOTIFY_SHAKE_ALERT
        NOTIFY_FOOD_QUALITY_ALERT       = 0x182e  #        - L0_I_NOTIFY_FOOD_QUALITY_ALERT
        NOTIFY_ERRORS                   = 0x182f  #        - L0_I_NOTIFY_ERRORS
        NOTIFY_FILTER_PAD_ALERT         = 0x1833  #        - L0_I_NOTIFY_FILTER_PAD_ALERT
        NOTIFY_EXPORT_STARTED           = 0x1831  #        - L0_I_NOTIFY_EXPORT_STARTED
        NOTIFY_EXPORT_ENDED             = 0x1832  #        - L0_I_NOTIFY_EXPORT_ENDED
        NOTIFY_EXPORT_PROGRESS          = 0x1835  #        - L0_I_NOTIFY_EXPORT_PROGRESS
        NOTIFY_EXPORT_CANCELLED         = 0x1834  #        - L0_I_NOTIFY_EXPORT_CANCELLED
        NOTIFY_START_WELL_WIZARD        = 0x1836  # TPDO55 - L0_I_NOTIFY_START_WELL_WIZARD
        NOTIFY_WELL_WIZARD_STATUS       = 0x1837  # TPDO56 - L0_I_NOTIFY_WELL_WIZARD_STATUS
    class PeriodicMessage:
        PRD_BOARD_STATUS                = 0x1802  # TPDO3  - L0_I_CONTROL_BRD_STATUS (periodic)
        PRD_IO_STATS                    = 0x1800  # TPDO1  - L0_I_CONTROL_BRD_IO_STATS (periodic)
        PRD_RTC_DATE_TIME               = 0x1801  # TPDO2  - L0_I_RTC_DATE_TIME (periodic)
    class DataMessage:
        DATA_MODE_STATE                 = 0x2022  #        - L0_I_MODESTATE

# ===========================================================================
# Line 1 (FDCAN2) COB-ID constants (CB <-> OMS)
# ===========================================================================
class L1_OMS_COB:
    class ResponseMessage:
        RSP_SELECTOR_VALVE              = 0x1400  # RPDO1  - OMS selector valve destination reached
        RSP_FILTER_PUMP                 = 0x1401  # RPDO2  - OMS filter pump state
        RSP_DRAIN_VALVE                 = 0x1402  # RPDO3  - OMS drain valve state
        RSP_TOKEN_GRANT                 = 0x1403  # RPDO4  - OMS token grant response
        RSP_TOKEN_RELEASE_ACK           = 0x1404  # RPDO5  - OMS token release ack
        RSP_VERSION                     = 0x1406  # RPDO7  - OMS version info response
        RSP_WELL_WIZARD_START           = 0x140b  # RPDO12 - OMS well wizard start response
        RSP_SERIAL_NUMBER_ACK           = 0x140f  #        - Serial number received ack
    class NotificationMessage:
        NOTIFY_DISPOSE_SWITCH           = 0x1405  # RPDO6  - L1_I_DISPOSE_SWITCH
        NOTIFY_BULK                     = 0x1407  #        - L1_I_OMS_BULK
        NOTIFY_USB_STATE                = 0x1408  # RPDO9  - L1_I_USB_STATE
        NOTIFY_WELL_WIZARD_STATUS       = 0x140c  # RPDO13 - OMS well wizard status
        NOTIFY_BULK_TANK_FULL           = 0x140d  # RPDO14 - L1_I_BULKTANKFULL
        NOTIFY_BULK_24VAC_INPUT         = 0x140e  # RPDO15 - L1_I_BULK_24VAC_INPUT
        NOTIFY_FILTER_PUMP_DEAD_HEAD    = 0x1410  # RPDO17 - L1_I_FILTER_PUMP_DEAD_HEAD
    class PeriodicMessage:
        PRD_BOARD_STATUS                = 0x140a  # RPDO11 - L1_I_OMS_BRD_STATUS (periodic)
    class DataMessage:
        DATA_BULK_TRANSFER_BUFFER       = 0x1409  # RPDO10 - L1_I_BULKTRANSFERBUFFER

class L1_CB_COB:
    class RequestMessage:
        REQ_OMS_VERSION                 = 0x1807  # TPDO8  - L1_I_REQUEST_BOARD_VERSION_INFO (OMS)
        REQ_WELL_WIZARD_START           = 0x1808  # TPDO9  - L1_I_CBTOOMS_REQUEST_START_WELL_WIZARD
        REQ_WELL_WIZARD_SET             = 0x180a  # TPDO11 - L1_I_CBTOOMS_REQUEST_WELL_WIZARD_SET
    class CommandMessage:
        CMD_SELECTOR_VALVE              = 0x1800  # TPDO1  - L1_I_SELECTORVALVE
        CMD_DRAIN_VALVE                 = 0x1801  # TPDO2  - L1_I_DRAINVALVE
        CMD_FILTER_PUMP                 = 0x1802  # TPDO3  - L1_I_FILTERPUMP
        CMD_ATO_PUMP                    = 0x1803  # TPDO4  - L1_I_ATOPUMP
        CMD_RTI_PUMP                    = 0x1806  # TPDO7  - L1_I_RTI_PUMP
    class TokenMessage:
        TOKEN_REQUEST                   = 0x1804  # TPDO5  - L1_I_TOKEN (CB requests token)
        TOKEN_RELEASE                   = 0x1805  # TPDO6  - L1_I_REQUESTRELEASEFILTERING
    class DataMessage:
        DATA_BULK_EXPORT_TRANSFER       = 0x1809  # TPDO10 - L1_I_BULK_EXPORT_TRANSFER_INFO
        DATA_SET_STRING                 = 0x180b  #        - L1_I_REQUEST_SET_STRING (serial number)


# ===========================================================================
# Line 0 - HIL -> CB command encoders and version helpers
# ===========================================================================
@dataclass(frozen=True)
class BoardVersionResponse:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def from_can(msg: CanMessage) -> "BoardVersionResponse":
        # Standard CANopen PDO packing: sub-index 1 → byte 0, 2 → byte 1, 3 → byte 2
        return BoardVersionResponse(major=msg.data[0],
                                    minor=msg.data[1],
                                    patch=msg.data[2],)


def encode_request_version() -> CanMessage:
    return CanMessage(arbitration_id=L0_HMI_COB.RequestMessage.REQ_BOARD_VERSION,
                      data=bytes(8),)


def encode_version_response(major: int, minor: int, patch: int) -> CanMessage:
    data = bytearray(8)
    data[0] = major
    data[1] = minor
    data[2] = patch
    return CanMessage(arbitration_id=L0_CB_COB.ResponseMessage.RSP_BOARD_VERSION,
                      data=bytes(data),)


@dataclass
class L0_RequestUiReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_UI_READY

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=bytes(8))


@dataclass
class L0_RequestPreheatStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_PREHEAT_START
    product_id: int = 0
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IB", self.product_id, self.vat),)


@dataclass
class L0_RequestPreheatStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_PREHEAT_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestCookTimerStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_COOK_TIMER_START
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_RequestCookTimerStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_COOK_TIMER_STOP
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_RequestCookTimerComplete:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_COOK_TIMER_COMPLETE
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_CommandVatOnOff:
    COB_ID: ClassVar[int] = L0_HMI_COB.CommandMessage.CMD_VAT_ON_OFF
    on: bool = True

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", 1 if self.on else 0),)


@dataclass
class L0_RequestEcoMode:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_ECO_MODE
    toggle: int = 1
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.toggle, self.vat),)


@dataclass
class L0_RequestRapidHeat:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_RAPID_HEAT
    toggle: int = 1
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.toggle, self.vat),)


@dataclass
class L0_RequestFryerShutdown:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FRYER_SHUTDOWN
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFilterPause:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILTER_PAUSE
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFilterResume:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILTER_RESUME
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFilterSkipStep:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILTER_SKIP_STEP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFilterStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILTER_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFilterDialogResponse:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILTER_DIALOG_RESPONSE
    vat: int = 0
    dialog: int = 0
    yes_no: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BBB", self.vat, self.dialog, self.yes_no),)


@dataclass
class L0_RequestExpressFilterLater:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_EXPRESS_FILTER_LATER
    vat: int = 0
    timer_ab: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.timer_ab),)


@dataclass
class L0_RequestExpressFilterReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_EXPRESS_FILTER_READY
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestExpressFilterStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_EXPRESS_FILTER_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDailyFilterLater:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DAILY_FILTER_LATER
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDailyFilterReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DAILY_FILTER_READY
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDailyFilterStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DAILY_FILTER_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFillSetSource:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILL_SET_SOURCE
    vat: int = 0
    fill_source: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.fill_source),)


@dataclass
class L0_RequestFillStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILL_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestFillStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_FILL_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDrainToPanStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DRAIN_TO_PAN_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDrainToPanStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DRAIN_TO_PAN_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDisposeStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DISPOSE_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestDisposeStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_DISPOSE_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestOilMgmtTaskStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_OIL_MGMT_TASK_START
    vat: int = 0
    task: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.task),)


@dataclass
class L0_RequestOilMgmtTaskEnd:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_OIL_MGMT_TASK_END
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_RequestClearError:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_CLEAR_ERROR
    error: int = 0
    action: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<HB", self.error, self.action),)


@dataclass
class L0_RequestProductNames:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_PRODUCT_NAMES
    locale: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<H", self.locale),)


@dataclass
class L0_RequestProductData:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_PRODUCT_DATA
    product_id: int = 0
    timer_set_in_secs: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<II", self.product_id, self.timer_set_in_secs),)


@dataclass
class L0_RequestUpdateSettings:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_UPDATE_SETTINGS

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=bytes(8),)


@dataclass
class L0_RequestWellWizardStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_START_WELL_WIZARD
    action: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.action),)


@dataclass
class L0_RequestWellWizardSet:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_WELL_WIZARD_SET
    id: int = 0
    screen: int = 0
    num: int = 0
    node_id: int = 0
    icon_state: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBBBB", self.id, self.screen, self.num, self.node_id, self.icon_state),)


@dataclass
class L0_RequestHmiBoardVersionInfo:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_BOARD_VERSION_INFO
    hmi_major: int = 0
    hmi_minor: int = 0
    hmi_patch: int = 0
    hmi_build: int = 0
    hmi_date_stamp: int = 0
    hmi_pcb_serial_num: int = 0
    cb_type_rev: int = 0
    hmi_micro_serial_num1: int = 0
    hmi_micro_serial_num2: int = 0
    hmi_micro_serial_num3: int = 0
    crank_major: int = 0
    crank_minor: int = 0
    crank_patch: int = 0
    crank_build: int = 0
    crank_date_stamp: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BBBHQQBIIIBBBHQ",
                                           self.hmi_major, self.hmi_minor, self.hmi_patch,
                                           self.hmi_build, self.hmi_date_stamp, self.hmi_pcb_serial_num,
                                           self.cb_type_rev,
                                           self.hmi_micro_serial_num1, self.hmi_micro_serial_num2, self.hmi_micro_serial_num3,
                                           self.crank_major, self.crank_minor, self.crank_patch,
                                           self.crank_build, self.crank_date_stamp,),)


# ===========================================================================
# Line 0 - CB -> HIL notification decoders
# ===========================================================================

@dataclass(frozen=True)
class L0_ResponseBackendReady:
    COB_ID: ClassVar[int] = L0_CB_COB.ResponseMessage.RSP_BACKEND_READY

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_ResponseBackendReady":
        return L0_ResponseBackendReady()


@dataclass(frozen=True)
class L0_NotificationPreheatStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_START
    product_id: int
    vat_temp: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationPreheatStarted":
        product_id, vat_temp, vat = struct.unpack_from("<IIB", msg.data)
        return L0_NotificationPreheatStarted(product_id=product_id, vat_temp=vat_temp, vat=vat)


@dataclass(frozen=True)
class L0_NotificationPreheatStopped:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_STOP
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationPreheatStopped":
        return L0_NotificationPreheatStopped(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationCookTimerStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_COOK_START
    product_id: int
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationCookTimerStarted":
        product_id, seconds, vat, timer = struct.unpack_from("<IIBB", msg.data)
        return L0_NotificationCookTimerStarted(product_id=product_id, seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotificationCookTimerStopped:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_COOK_STOP
    product_id: int
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationCookTimerStopped":
        product_id, seconds, vat, timer = struct.unpack_from("<IIBB", msg.data)
        return L0_NotificationCookTimerStopped(product_id=product_id, seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotificationPreheatUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_UPDATE
    vat_temp: int
    progress: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationPreheatUpdate":
        vat_temp, progress, vat = struct.unpack_from("<IBB", msg.data)
        return L0_NotificationPreheatUpdate(vat_temp=vat_temp, progress=progress, vat=vat)


@dataclass(frozen=True)
class L0_NotificationPreheatComplete:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_PREHEAT_COMPLETE
    vat_temp: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationPreheatComplete":
        vat_temp, vat = struct.unpack_from("<IB", msg.data)
        return L0_NotificationPreheatComplete(vat_temp=vat_temp, vat=vat)


@dataclass(frozen=True)
class L0_NotificationCookTimerUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_COOK_UPDATE
    product_id: int
    seconds: int
    vat: int
    timer: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationCookTimerUpdate":
        product_id, seconds, vat, timer, state = struct.unpack_from("<IIBBB", msg.data)
        return L0_NotificationCookTimerUpdate(product_id=product_id, seconds=seconds, vat=vat, timer=timer, state=state)


@dataclass(frozen=True)
class L0_NotificationFryerStartup:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FRYER_STARTUP

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFryerStartup":
        return L0_NotificationFryerStartup()


@dataclass(frozen=True)
class L0_NotificationShutdown:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_SHUTDOWN
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationShutdown":
        return L0_NotificationShutdown(vat=msg.data[0])


@dataclass(frozen=True)
class L0_PeriodicBoardStatus:
    COB_ID: ClassVar[int] = L0_CB_COB.PeriodicMessage.PRD_BOARD_STATUS
    vata_temp_current: int
    vata_temp_target: int
    vatb_temp_current: int
    vatb_temp_target: int
    basket1_cook_timer: int
    basket2_cook_timer: int
    basket3_cook_timer: int
    basket4_cook_timer: int
    shake_quality_bitflags: int
    cook_daily_filter_bitflags: int
    basket1_quality_timer: int
    basket2_quality_timer: int
    basket3_quality_timer: int
    basket4_quality_timer: int
    vata_modes: int
    vatb_modes: int
    vata_oil_used_pct: int
    vatb_oil_used_pct: int
    extra_bitflags: int
    status_error_num: int
    status_error_vat: int
    status_error_num_r: int
    status_error_vat_r: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PeriodicBoardStatus":
        (
            vata_tc, vata_tt, vatb_tc, vatb_tt,
            b1_ct, b2_ct, b3_ct, b4_ct,
            sq_flags, cdf_flags,
            b1_qt, b2_qt, b3_qt, b4_qt,
            vata_modes, vatb_modes, vata_oil, vatb_oil, extra,
            err_num, err_vat, err_num_r, err_vat_r,
        ) = struct.unpack_from("<4H4h2B4h5BHBHB", msg.data)
        return L0_PeriodicBoardStatus(
            vata_temp_current=vata_tc, vata_temp_target=vata_tt,
            vatb_temp_current=vatb_tc, vatb_temp_target=vatb_tt,
            basket1_cook_timer=b1_ct, basket2_cook_timer=b2_ct,
            basket3_cook_timer=b3_ct, basket4_cook_timer=b4_ct,
            shake_quality_bitflags=sq_flags, cook_daily_filter_bitflags=cdf_flags,
            basket1_quality_timer=b1_qt, basket2_quality_timer=b2_qt,
            basket3_quality_timer=b3_qt, basket4_quality_timer=b4_qt,
            vata_modes=vata_modes, vatb_modes=vatb_modes,
            vata_oil_used_pct=vata_oil, vatb_oil_used_pct=vatb_oil,
            extra_bitflags=extra,
            status_error_num=err_num, status_error_vat=err_vat,
            status_error_num_r=err_num_r, status_error_vat_r=err_vat_r,
        )


@dataclass(frozen=True)
class L0_PeriodicIoStats:
    COB_ID: ClassVar[int] = L0_CB_COB.PeriodicMessage.PRD_IO_STATS
    active: int
    line_voltage: int
    line_current: int
    v24vac_voltage: int
    v24vac_current: int
    rectified_24vac: int
    v12vdc: int
    v5vdc: int
    v3_3vdc: int
    pcb_temp: int
    pressure1: int
    pressure2: int
    audio_flag: int
    sdcard_flag: int
    flash_flag: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PeriodicIoStats":
        (
            active, line_v, line_c, v24vac_v, v24vac_c,
            rect24vac, v12, v5, v3_3, pcb, p1, p2,
            audio, sdcard, flash,
        ) = struct.unpack_from("<b11H3B", msg.data)
        return L0_PeriodicIoStats(
            active=active, line_voltage=line_v, line_current=line_c,
            v24vac_voltage=v24vac_v, v24vac_current=v24vac_c,
            rectified_24vac=rect24vac, v12vdc=v12, v5vdc=v5, v3_3vdc=v3_3,
            pcb_temp=pcb, pressure1=p1, pressure2=p2,
            audio_flag=audio, sdcard_flag=sdcard, flash_flag=flash,
        )


@dataclass(frozen=True)
class L0_PeriodicRtcDateTime:
    COB_ID: ClassVar[int] = L0_CB_COB.PeriodicMessage.PRD_RTC_DATE_TIME
    weekday: int
    month: int
    date: int
    year: int
    hours: int
    minutes: int
    seconds: int
    time_format: int
    update_rtc_flag: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PeriodicRtcDateTime":
        weekday, month, date, year, hours, minutes, seconds, time_format, update_rtc_flag = (
            struct.unpack_from("<9B", msg.data)
        )
        return L0_PeriodicRtcDateTime(
            weekday=weekday, month=month, date=date, year=year,
            hours=hours, minutes=minutes, seconds=seconds,
            time_format=time_format, update_rtc_flag=update_rtc_flag,
        )


@dataclass(frozen=True)
class L0_DataModeState:
    COB_ID: ClassVar[int] = L0_CB_COB.DataMessage.DATA_MODE_STATE
    name_enum: int
    mode_type: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_DataModeState":
        name_enum, mode_type = struct.unpack_from("<HH", msg.data)
        return L0_DataModeState(name_enum=name_enum, mode_type=mode_type)


@dataclass(frozen=True)
class L0_NotificationEcoMode:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_ECO_MODE
    toggle: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationEcoMode":
        toggle, vat = struct.unpack_from("<BB", msg.data)
        return L0_NotificationEcoMode(toggle=toggle, vat=vat)


@dataclass(frozen=True)
class L0_NotificationRapidHeat:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_RAPID_HEAT
    toggle: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationRapidHeat":
        toggle, vat = struct.unpack_from("<BB", msg.data)
        return L0_NotificationRapidHeat(toggle=toggle, vat=vat)


@dataclass(frozen=True)
class L0_NotificationHpunitSettings:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_HPUNIT_SETTINGS
    raw: bytes = b""

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationHpunitSettings":
        return L0_NotificationHpunitSettings(raw=bytes(msg.data))


@dataclass(frozen=True)
class L0_NotificationFilterPause:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_PAUSE
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterPause":
        return L0_NotificationFilterPause(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationFilterResume:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_RESUME
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterResume":
        return L0_NotificationFilterResume(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationFilterSkipStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_SKIP_STEP
    vat: int
    step: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterSkipStep":
        vat, step = struct.unpack_from("<BB", msg.data)
        return L0_NotificationFilterSkipStep(vat=vat, step=step)


@dataclass(frozen=True)
class L0_NotificationFilterFinished:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_FINISHED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterFinished":
        return L0_NotificationFilterFinished(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationFilterStop:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_STOP
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterStop":
        return L0_NotificationFilterStop(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationExpressFilterAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExpressFilterAlert":
        return L0_NotificationExpressFilterAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationExpressFilterLater:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_LATER
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExpressFilterLater":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotificationExpressFilterLater(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotificationExpressFilterReady:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_READY
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExpressFilterReady":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotificationExpressFilterReady(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotificationExpressFilterStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_STARTED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExpressFilterStarted":
        return L0_NotificationExpressFilterStarted(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationExpressFilterStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPRESS_FILTER_STEP
    vat: int
    step: int
    step_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExpressFilterStep":
        vat, step, step_state = struct.unpack_from("<BBB", msg.data)
        return L0_NotificationExpressFilterStep(vat=vat, step=step, step_state=step_state)


@dataclass(frozen=True)
class L0_NotificationDailyFilterAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationDailyFilterAlert":
        return L0_NotificationDailyFilterAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationDailyFilterLater:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_LATER
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationDailyFilterLater":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotificationDailyFilterLater(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotificationDailyFilterReady:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_READY
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationDailyFilterReady":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotificationDailyFilterReady(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotificationDailyFilterStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_STARTED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationDailyFilterStarted":
        return L0_NotificationDailyFilterStarted(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationDailyFilterStepUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_DAILY_FILTER_STEP_UPDATE
    vat: int
    step: int
    step_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationDailyFilterStepUpdate":
        vat, step, step_state = struct.unpack_from("<BBB", msg.data)
        return L0_NotificationDailyFilterStepUpdate(vat=vat, step=step, step_state=step_state)


@dataclass(frozen=True)
class L0_NotificationValveState:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_VALVE_STATE
    vat: int
    valve: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationValveState":
        vat, valve, state = struct.unpack_from("<BBB", msg.data)
        return L0_NotificationValveState(vat=vat, valve=valve, state=state)


@dataclass(frozen=True)
class L0_NotificationOilMgmtTaskStart:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_OIL_MGMT_TASK_START
    vat: int
    task: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationOilMgmtTaskStart":
        vat, task, ok = struct.unpack_from("<BBB", msg.data)
        return L0_NotificationOilMgmtTaskStart(vat=vat, task=task, ok=ok)


@dataclass(frozen=True)
class L0_NotificationOilMgmtTaskEnd:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_OIL_MGMT_TASK_END
    vat: int
    task: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationOilMgmtTaskEnd":
        vat, task, ok = struct.unpack_from("<BBB", msg.data)
        return L0_NotificationOilMgmtTaskEnd(vat=vat, task=task, ok=ok)


@dataclass(frozen=True)
class L0_NotificationOilMgmtStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_OIL_MGMT_STEP
    step: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationOilMgmtStep":
        step, vat = struct.unpack_from("<HB", msg.data)
        return L0_NotificationOilMgmtStep(step=step, vat=vat)


@dataclass(frozen=True)
class L0_NotificationRearDisposeCountdown:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_REAR_DISPOSE_COUNTDOWN
    seconds: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationRearDisposeCountdown":
        seconds, vat = struct.unpack_from("<IB", msg.data)
        return L0_NotificationRearDisposeCountdown(seconds=seconds, vat=vat)


@dataclass(frozen=True)
class L0_NotificationShakeAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_SHAKE_ALERT
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationShakeAlert":
        vat, timer = struct.unpack_from("<BB", msg.data)
        return L0_NotificationShakeAlert(vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotificationFoodQualityAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FOOD_QUALITY_ALERT
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFoodQualityAlert":
        seconds, vat, timer = struct.unpack_from("<IBB", msg.data)
        return L0_NotificationFoodQualityAlert(seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotificationErrors:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_ERRORS
    id_number: int
    vat: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationErrors":
        id_number, vat, state = struct.unpack_from("<IBB", msg.data)
        return L0_NotificationErrors(id_number=id_number, vat=vat, state=state)


@dataclass(frozen=True)
class L0_NotificationFilterPadAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_FILTER_PAD_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationFilterPadAlert":
        return L0_NotificationFilterPadAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationExportStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPORT_STARTED

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExportStarted":
        return L0_NotificationExportStarted()


@dataclass(frozen=True)
class L0_NotificationExportEnded:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPORT_ENDED
    success: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExportEnded":
        return L0_NotificationExportEnded(success=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationExportProgress:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPORT_PROGRESS
    total: int
    done: int
    overall_pct: int
    curfile_pct: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExportProgress":
        total, done, overall_pct, curfile_pct = struct.unpack_from("<QQBB", msg.data)
        return L0_NotificationExportProgress(total=total, done=done, overall_pct=overall_pct, curfile_pct=curfile_pct)


@dataclass(frozen=True)
class L0_NotificationExportCancelled:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_EXPORT_CANCELLED

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationExportCancelled":
        return L0_NotificationExportCancelled()


@dataclass(frozen=True)
class L0_NotificationStartWellWizard:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_START_WELL_WIZARD
    action: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationStartWellWizard":
        return L0_NotificationStartWellWizard(action=msg.data[0])


@dataclass(frozen=True)
class L0_NotificationWellWizardStatus:
    COB_ID: ClassVar[int] = L0_CB_COB.NotificationMessage.NOTIFY_WELL_WIZARD_STATUS
    well_id1: int
    well_id2: int
    well_id3: int
    well_id4: int
    screen: int
    well_count: int
    well_num1: int
    well_num2: int
    well_num3: int
    well_num4: int
    node_id1: int
    node_id2: int
    node_id3: int
    node_id4: int
    icon_state1: int
    icon_state2: int
    icon_state3: int
    icon_state4: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotificationWellWizardStatus":
        (
            wid1, wid2, wid3, wid4,
            screen, well_count,
            wn1, wn2, wn3, wn4,
            nid1, nid2, nid3, nid4,
            is1, is2, is3, is4,
        ) = struct.unpack_from("<4I14B", msg.data)
        return L0_NotificationWellWizardStatus(
            well_id1=wid1, well_id2=wid2, well_id3=wid3, well_id4=wid4,
            screen=screen, well_count=well_count,
            well_num1=wn1, well_num2=wn2, well_num3=wn3, well_num4=wn4,
            node_id1=nid1, node_id2=nid2, node_id3=nid3, node_id4=nid4,
            icon_state1=is1, icon_state2=is2, icon_state3=is3, icon_state4=is4,
        )


# ===========================================================================
# Line 1 - HIL (OMS emulation) -> CB message encoders
# ===========================================================================

@dataclass
class L1_ResponseSelectorValve:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_SELECTOR_VALVE
    destination_reached: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.destination_reached),)


@dataclass
class L1_ResponseDrainValve:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_DRAIN_VALVE
    number: int = 0
    open: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.number, self.open),)


@dataclass
class L1_ResponseFilterPump:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_FILTER_PUMP
    on: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.on),)


@dataclass
class L1_ResponseTokenGrant:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_TOKEN_GRANT
    id_low: int = 0
    id_high: int = 0
    allowed: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIB", self.id_low, self.id_high, self.allowed),)


@dataclass
class L1_ResponseTokenReleaseAck:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_TOKEN_RELEASE_ACK
    id_low: int = 0
    id_high: int = 0
    request: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIB", self.id_low, self.id_high, self.request),)


@dataclass
class L1_NotificationDisposeSwitchState:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_DISPOSE_SWITCH
    open: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.open),)


@dataclass
class L1_NotificationUsbState:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_USB_STATE
    usb_status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.usb_status),)


@dataclass
class L1_ResponseOmsVersion:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_VERSION
    major: int = 0
    minor: int = 0
    patch: int = 0
    build: int = 0
    date_stamp: int = 0
    pcb_serial_num: int = 0
    type_rev: int = 0
    micro_serial_num1: int = 0
    micro_serial_num2: int = 0
    micro_serial_num3: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BBBHQQBIII",
                                           self.major, self.minor, self.patch, self.build,
                                           self.date_stamp, self.pcb_serial_num, self.type_rev,
                                           self.micro_serial_num1, self.micro_serial_num2, self.micro_serial_num3,),)


@dataclass
class L1_NotificationOmsBulk:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_BULK
    operation: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.operation),)


@dataclass
class L1_DataBulkTransferBuffer:
    COB_ID: ClassVar[int] = L1_OMS_COB.DataMessage.DATA_BULK_TRANSFER_BUFFER
    data1: int = 0
    data2: int = 0
    field1: int = 0
    field2: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIBB", self.data1, self.data2, self.field1, self.field2),)


@dataclass
class L1_PeriodicOmsBoardStatus:
    COB_ID: ClassVar[int] = L1_OMS_COB.PeriodicMessage.PRD_BOARD_STATUS
    voltage_24v: int = 0
    voltage_12v: int = 0
    voltage_3_3v: int = 0
    voltage_5v: int = 0
    usb_connection_status: int = 0
    filter_pump_status: int = 0
    dispose_switch_status: int = 0
    board_temperature: int = 0
    drain_pan_switch_status: int = 0
    error_codes: int = 0
    filter_pump_current: int = 0
    token_owner: int = 0
    rti_connected_status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<4H3BH2BH2B",
                                           self.voltage_24v, self.voltage_12v, self.voltage_3_3v, self.voltage_5v,
                                           self.usb_connection_status, self.filter_pump_status, self.dispose_switch_status,
                                           self.board_temperature,
                                           self.drain_pan_switch_status, self.error_codes,
                                           self.filter_pump_current,
                                           self.token_owner, self.rti_connected_status,),)


@dataclass
class L1_ResponseOmsWellWizardStart:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_WELL_WIZARD_START
    action: int = 0
    chip_id: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BI", self.action, self.chip_id),)


@dataclass
class L1_NotificationOmsWellWizardStatus:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_WELL_WIZARD_STATUS
    well_id1: int = 0
    well_id2: int = 0
    well_id3: int = 0
    well_id4: int = 0
    screen: int = 0
    well_count: int = 0
    well_num1: int = 0
    well_num2: int = 0
    well_num3: int = 0
    well_num4: int = 0
    node_id1: int = 0
    node_id2: int = 0
    node_id3: int = 0
    node_id4: int = 0
    icon_state1: int = 0
    icon_state2: int = 0
    icon_state3: int = 0
    icon_state4: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<4I14B",
                                           self.well_id1, self.well_id2, self.well_id3, self.well_id4,
                                           self.screen, self.well_count,
                                           self.well_num1, self.well_num2, self.well_num3, self.well_num4,
                                           self.node_id1, self.node_id2, self.node_id3, self.node_id4,
                                           self.icon_state1, self.icon_state2, self.icon_state3, self.icon_state4,),)


@dataclass
class L1_NotificationBulkTankFull:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_BULK_TANK_FULL
    bulk_status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.bulk_status),)


@dataclass
class L1_NotificationBulk24VacInput:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_BULK_24VAC_INPUT
    status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.status),)


@dataclass
class L1_ResponseSerialNumberAck:
    COB_ID: ClassVar[int] = L1_OMS_COB.ResponseMessage.RSP_SERIAL_NUMBER_ACK
    ack: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.ack),)


@dataclass
class L1_NotificationFilterPumpDeadHead:
    COB_ID: ClassVar[int] = L1_OMS_COB.NotificationMessage.NOTIFY_FILTER_PUMP_DEAD_HEAD
    detected: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.detected),)


# ===========================================================================
# Line 1 - CB -> HIL command decoders
# ===========================================================================

@dataclass(frozen=True)
class L1_CommandSelectorValve:
    COB_ID: ClassVar[int] = L1_CB_COB.CommandMessage.CMD_SELECTOR_VALVE
    port: int
    destination_reached: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CommandSelectorValve":
        port, destination_reached, token_id = struct.unpack_from("<BBB", msg.data)
        return L1_CommandSelectorValve(port=port, destination_reached=destination_reached, token_id=token_id)


@dataclass(frozen=True)
class L1_CommandDrainValveCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.CommandMessage.CMD_DRAIN_VALVE
    valve_number: int
    open_: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CommandDrainValveCmd":
        valve_number, open_, token_id = struct.unpack_from("<BBB", msg.data)
        return L1_CommandDrainValveCmd(valve_number=valve_number, open_=open_, token_id=token_id)


@dataclass(frozen=True)
class L1_CommandFilterPump:
    COB_ID: ClassVar[int] = L1_CB_COB.CommandMessage.CMD_FILTER_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CommandFilterPump":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_CommandFilterPump(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_TokenRequest:
    COB_ID: ClassVar[int] = L1_CB_COB.TokenMessage.TOKEN_REQUEST
    id_low: int
    id_high: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_TokenRequest":
        id_low, id_high, token_id = struct.unpack_from("<IIB", msg.data)
        return L1_TokenRequest(id_low=id_low, id_high=id_high, token_id=token_id)


@dataclass(frozen=True)
class L1_TokenRelease:
    COB_ID: ClassVar[int] = L1_CB_COB.TokenMessage.TOKEN_RELEASE
    token_id: int
    id_low: int
    id_high: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_TokenRelease":
        token_id, id_low, id_high = struct.unpack_from("<BII", msg.data)
        return L1_TokenRelease(token_id=token_id, id_low=id_low, id_high=id_high)


@dataclass(frozen=True)
class L1_CommandAtoPump:
    COB_ID: ClassVar[int] = L1_CB_COB.CommandMessage.CMD_ATO_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CommandAtoPump":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_CommandAtoPump(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_CommandRtiPump:
    COB_ID: ClassVar[int] = L1_CB_COB.CommandMessage.CMD_RTI_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CommandRtiPump":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_CommandRtiPump(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_RequestOmsVersion:
    COB_ID: ClassVar[int] = L1_CB_COB.RequestMessage.REQ_OMS_VERSION
    trigger: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_RequestOmsVersion":
        return L1_RequestOmsVersion(trigger=msg.data[0] if msg.data else 0)


@dataclass(frozen=True)
class L1_RequestCbToOmsWellWizardStart:
    COB_ID: ClassVar[int] = L1_CB_COB.RequestMessage.REQ_WELL_WIZARD_START
    action: int
    chip_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_RequestCbToOmsWellWizardStart":
        action, chip_id = struct.unpack_from("<BI", msg.data)
        return L1_RequestCbToOmsWellWizardStart(action=action, chip_id=chip_id)


@dataclass(frozen=True)
class L1_DataBulkExportTransfer:
    COB_ID: ClassVar[int] = L1_CB_COB.DataMessage.DATA_BULK_EXPORT_TRANSFER
    field1: int
    field2: int
    data1: int
    data2: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_DataBulkExportTransfer":
        field1, field2, data1, data2 = struct.unpack_from("<BBII", msg.data)
        return L1_DataBulkExportTransfer(field1=field1, field2=field2, data1=data1, data2=data2)


@dataclass(frozen=True)
class L1_RequestCbToOmsWellWizardSet:
    COB_ID: ClassVar[int] = L1_CB_COB.RequestMessage.REQ_WELL_WIZARD_SET
    id: int
    screen: int
    num: int
    node_id: int
    icon_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_RequestCbToOmsWellWizardSet":
        id_, screen, num, node_id, icon_state = struct.unpack_from("<IBBBB", msg.data)
        return L1_RequestCbToOmsWellWizardSet(id=id_, screen=screen, num=num, node_id=node_id, icon_state=icon_state)


@dataclass(frozen=True)
class L1_DataSetString:
    COB_ID: ClassVar[int] = L1_CB_COB.DataMessage.DATA_SET_STRING
    trigger: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_DataSetString":
        return L1_DataSetString(trigger=msg.data[0] if msg.data else 0)


@dataclass
class L0_RequestBoardVersion:
    COB_ID: ClassVar[int] = L0_HMI_COB.RequestMessage.REQ_BOARD_VERSION

    def encode(self) -> CanMessage:
        return encode_request_version()


class L0_HMI_RequestMessages:
    RequestBoardVersion                 = L0_RequestBoardVersion
    RequestUiReady                      = L0_RequestUiReady
    RequestPreheatStart                 = L0_RequestPreheatStart
    RequestPreheatStop                  = L0_RequestPreheatStop
    RequestCookTimerStart               = L0_RequestCookTimerStart
    RequestCookTimerStop                = L0_RequestCookTimerStop
    RequestCookTimerComplete            = L0_RequestCookTimerComplete
    RequestEcoMode                      = L0_RequestEcoMode
    RequestRapidHeat                    = L0_RequestRapidHeat
    RequestFryerShutdown                = L0_RequestFryerShutdown
    RequestFilterPause                  = L0_RequestFilterPause
    RequestFilterResume                 = L0_RequestFilterResume
    RequestFilterSkipStep               = L0_RequestFilterSkipStep
    RequestFilterStop                   = L0_RequestFilterStop
    RequestFilterDialogResponse         = L0_RequestFilterDialogResponse
    RequestExpressFilterLater           = L0_RequestExpressFilterLater
    RequestExpressFilterReady           = L0_RequestExpressFilterReady
    RequestExpressFilterStart           = L0_RequestExpressFilterStart
    RequestDailyFilterLater             = L0_RequestDailyFilterLater
    RequestDailyFilterReady             = L0_RequestDailyFilterReady
    RequestDailyFilterStart             = L0_RequestDailyFilterStart
    RequestFillSetSource                = L0_RequestFillSetSource
    RequestFillStart                    = L0_RequestFillStart
    RequestFillStop                     = L0_RequestFillStop
    RequestDrainToPanStart              = L0_RequestDrainToPanStart
    RequestDrainToPanStop               = L0_RequestDrainToPanStop
    RequestDisposeStart                 = L0_RequestDisposeStart
    RequestDisposeStop                  = L0_RequestDisposeStop
    RequestOilMgmtTaskStart             = L0_RequestOilMgmtTaskStart
    RequestOilMgmtTaskEnd               = L0_RequestOilMgmtTaskEnd
    RequestClearError                   = L0_RequestClearError
    RequestProductNamesRequest          = L0_RequestProductNames
    RequestProductDataRequest           = L0_RequestProductData
    RequestUpdateSettings               = L0_RequestUpdateSettings
    RequestWellWizardStart              = L0_RequestWellWizardStart
    RequestWellWizardSet                = L0_RequestWellWizardSet
    RequestHmiBoardVersionInfo          = L0_RequestHmiBoardVersionInfo


class L0_HMI_CommandMessages:
    CommandVatOnOff = L0_CommandVatOnOff

class L0_CB_ResponseMessages:
    ResponseBackendReady                = L0_ResponseBackendReady

class L0_CB_NotificationMessages:
    NotificationFryerStartup            = L0_NotificationFryerStartup
    NotificationShutdown                = L0_NotificationShutdown
    PeriodicBoardStatus                 = L0_PeriodicBoardStatus
    PeriodicIoStats                     = L0_PeriodicIoStats
    PeriodicRtcDateTime                 = L0_PeriodicRtcDateTime
    DataModeState                       = L0_DataModeState
    NotificationPreheatStarted          = L0_NotificationPreheatStarted
    NotificationPreheatStopped          = L0_NotificationPreheatStopped
    NotificationPreheatUpdate           = L0_NotificationPreheatUpdate
    NotificationPreheatComplete         = L0_NotificationPreheatComplete
    NotificationCookTimerStarted        = L0_NotificationCookTimerStarted
    NotificationCookTimerStopped        = L0_NotificationCookTimerStopped
    NotificationCookTimerUpdate         = L0_NotificationCookTimerUpdate
    NotificationEcoMode                 = L0_NotificationEcoMode
    NotificationRapidHeat               = L0_NotificationRapidHeat
    NotificationHpunitSettings          = L0_NotificationHpunitSettings
    NotificationFilterPause             = L0_NotificationFilterPause
    NotificationFilterResume            = L0_NotificationFilterResume
    NotificationFilterSkipStep          = L0_NotificationFilterSkipStep
    NotificationFilterFinished          = L0_NotificationFilterFinished
    NotificationFilterStop              = L0_NotificationFilterStop
    NotificationExpressFilterAlert      = L0_NotificationExpressFilterAlert
    NotificationExpressFilterLater      = L0_NotificationExpressFilterLater
    NotificationExpressFilterReady      = L0_NotificationExpressFilterReady
    NotificationExpressFilterStarted    = L0_NotificationExpressFilterStarted
    NotificationExpressFilterStep       = L0_NotificationExpressFilterStep
    NotificationDailyFilterAlert        = L0_NotificationDailyFilterAlert
    NotificationDailyFilterLater        = L0_NotificationDailyFilterLater
    NotificationDailyFilterReady        = L0_NotificationDailyFilterReady
    NotificationDailyFilterStarted      = L0_NotificationDailyFilterStarted
    NotificationDailyFilterStepUpdate   = L0_NotificationDailyFilterStepUpdate
    NotificationValveState              = L0_NotificationValveState
    NotificationOilMgmtTaskStart        = L0_NotificationOilMgmtTaskStart
    NotificationOilMgmtTaskEnd          = L0_NotificationOilMgmtTaskEnd
    NotificationOilMgmtStep             = L0_NotificationOilMgmtStep
    NotificationRearDisposeCountdown    = L0_NotificationRearDisposeCountdown
    NotificationShakeAlert              = L0_NotificationShakeAlert
    NotificationFoodQualityAlert        = L0_NotificationFoodQualityAlert
    NotificationErrors                  = L0_NotificationErrors
    NotificationFilterPadAlert          = L0_NotificationFilterPadAlert
    NotificationExportStarted           = L0_NotificationExportStarted
    NotificationExportEnded             = L0_NotificationExportEnded
    NotificationExportProgress          = L0_NotificationExportProgress
    NotificationExportCancelled         = L0_NotificationExportCancelled
    NotificationStartWellWizard         = L0_NotificationStartWellWizard
    NotificationWellWizardStatus        = L0_NotificationWellWizardStatus


class L1_OMS_ResponseMessages:
    ResponseSelectorValve               = L1_ResponseSelectorValve
    ResponseDrainValve                  = L1_ResponseDrainValve
    ResponseFilterPump                  = L1_ResponseFilterPump
    ResponseTokenGrant                  = L1_ResponseTokenGrant
    ResponseTokenReleaseAck             = L1_ResponseTokenReleaseAck
    ResponseOmsVersion                  = L1_ResponseOmsVersion
    ResponseOmsWellWizardStart          = L1_ResponseOmsWellWizardStart
    ResponseSerialNumberAck             = L1_ResponseSerialNumberAck
    

class L1_OMS_NotificationMessages:
    NotificationDisposeSwitchState     = L1_NotificationDisposeSwitchState
    NotificationUsbState               = L1_NotificationUsbState
    NotificationOmsBulk                = L1_NotificationOmsBulk
    NotificationOmsWellWizardStatus    = L1_NotificationOmsWellWizardStatus
    NotificationBulkTankFull           = L1_NotificationBulkTankFull
    NotificationBulk24VacInput         = L1_NotificationBulk24VacInput
    NotificationFilterPumpDeadHead     = L1_NotificationFilterPumpDeadHead


class L1_OMS_DataMessages:
    DataBulkTransferBuffer             = L1_DataBulkTransferBuffer


class L1_OMS_PeriodicMessages:
    PeriodicOmsBoardStatus             = L1_PeriodicOmsBoardStatus


class L1_CB_RequestMessages:
    RequestOmsVersion                  = L1_RequestOmsVersion
    RequestCbToOmsWellWizardStart      = L1_RequestCbToOmsWellWizardStart
    RequestCbToOmsWellWizardSet        = L1_RequestCbToOmsWellWizardSet


class L1_CB_CommandMessages:
    CommandSelectorValve               = L1_CommandSelectorValve
    CommandDrainValve                  = L1_CommandDrainValveCmd
    CommandFilterPump                  = L1_CommandFilterPump
    CommandAtoPump                     = L1_CommandAtoPump
    CommandRtiPump                     = L1_CommandRtiPump
    

class L1_CB_TokenMessages:
    TokenRequest                       = L1_TokenRequest
    TokenRelease                       = L1_TokenRelease


class L1_CB_DataMessages:
    DataBulkExportTransfer             = L1_DataBulkExportTransfer
    DataSetString                      = L1_DataSetString
