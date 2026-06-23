from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import ClassVar

from common.can_interface import CanMessage


# ===========================================================================
# Line 0 (FDCAN1) COB-ID constants (CB <-> HMI)
# ===========================================================================
class L0_HMI_COB:
    REQUEST_BOARD_VERSION              = 0x143a  # RPDO57 - L0_I_REQUEST_BOARD_VERSION_INFO
    UI_READY                           = 0x1429  # RPDO26 - L0_I_REQUEST_UI_READY1
    BOARD_VERSION_INFO                 = 0x1437  # RPDO56 - L0_I_HMI_BOARD_VERSION_INFO
    PREHEAT_START                      = 0x1408  # RPDO25 - L0_I_REQUEST_PREHEAT_START
    PREHEAT_STOP                       = 0x1409  # RPDO26 - L0_I_REQUEST_PREHEAT_STOP
    COOK_TIMER_START                   = 0x1401  # RPDO2  - L0_I_REQUEST_COOK_TIMER_START
    COOK_TIMER_STOP                    = 0x1402  # RPDO3  - L0_I_REQUEST_COOK_TIMER_STOP
    COOK_TIMER_COMPLETE                = 0x1406  # RPDO7  - L0_I_REQUEST_COOK_TIMER_COMPLETE
    VAT_ON_OFF                         = 0x2062  #        - L0_I_CMDVATONOFF
    ECO_MODE                           = 0x140a  # RPDO11 - L0_I_REQUEST_ECO_MODE
    RAPID_HEAT                         = 0x140b  # RPDO12 - L0_I_REQUEST_RAPID_HEAT
    UPDATE_SETTINGS                    = 0x142a  # RPDO27 - L0_I_REQUEST_UPDATE_SETTINGS
    FRYER_SHUTDOWN                     = 0x1405  # RPDO6  - L0_I_RECEIVE_PDO_REQUEST_FRYER_SHUTDOWN
    FILTER_PAUSE                       = 0x140e  # RPDO15 - L0_I_REQUEST_FILTER_PAUSE
    FILTER_RESUME                      = 0x140f  # RPDO16 - L0_I_REQUEST_FILTER_RESUME
    FILTER_SKIP_STEP                   = 0x1410  # RPDO17 - L0_I_REQUEST_FILTER_SKIP_STEP
    FILTER_STOP                        = 0x1413  # RPDO20 - L0_I_REQUEST_FILTER_STOP
    FILTER_DIALOG_RESPONSE             = 0x1428  # RPDO41 - L0_I_REQUEST_FILTER_DIALOG_RESPONSE
    EXPRESS_FILTER_LATER               = 0x1414  #        - L0_I_REQUEST_EXPRESS_FILTER_LATER
    EXPRESS_FILTER_READY               = 0x1415  #        - L0_I_REQUEST_EXPRESS_FILTER_READY
    EXPRESS_FILTER_START               = 0x1416  #        - L0_I_REQUEST_EXPRESS_FILTER_START
    DAILY_FILTER_LATER                 = 0x1417  #        - L0_I_REQUEST_DAILY_FILTER_LATER
    DAILY_FILTER_READY                 = 0x1418  #        - L0_I_REQUEST_DAILY_FILTER_READY
    DAILY_FILTER_START                 = 0x1446  #        - L0_I_REQUEST_DAILY_FILTER_START
    FILL_SET_SOURCE                    = 0x1419  #        - L0_I_REQUEST_FILL_SET_SOURCE
    FILL_START                         = 0x141a  #        - L0_I_REQUEST_FILL_START
    FILL_STOP                          = 0x141b  #        - L0_I_REQUEST_FILL_STOP
    DRAIN_TO_PAN_START                 = 0x1420  #        - L0_I_REQUEST_DRAIN_TO_PAN_START
    DRAIN_TO_PAN_STOP                  = 0x1421  #        - L0_I_REQUEST_DRAIN_TO_PAN_STOP
    DISPOSE_START                      = 0x1423  #        - L0_I_REQUEST_DISPOSE_START
    DISPOSE_STOP                       = 0x1424  #        - L0_I_REQUEST_DISPOSE_STOP
    OIL_MGMT_TASK_START                = 0x142b  # RPDO29 - L0_I_REQUEST_START_OIL_MANAGEMENT_TASK
    OIL_MGMT_TASK_END                  = 0x1434  # RPDO55 - L0_I_REQUEST_END_OIL_MANAGEMENT_TASK
    CLEAR_ERROR                        = 0x1440  # RPDO65 - L0_I_REQUEST_CLEAR_ERROR
    PRODUCT_NAMES                      = 0x142d  #        - L0_I_REQUEST_PRODUCT_NAMES
    PRODUCT_DATA                       = 0x142e  #        - L0_I_REQUEST_PRODUCT_DATA
    START_WELL_WIZARD                  = 0x1444  # RPDO69 - L0_I_REQUEST_START_WELL_WIZARD
    WELL_WIZARD_SET                    = 0x1445  # RPDO70 - L0_I_REQUEST_WELL_WIZARD_SET
        
class L0_CB_COB:
    RECEIVED_BOARD_VERSION              = 0x1830  # TPDO49 - L0_I_RECEIVED_BOARD_VERSION_INFO
    BACKEND_READY                       = 0x1829  # TPDO42 - L0_I_BACKEND_READY
    NOTIFY_FRYER_STARTUP                = 0x180c  #        - L0_I_TRANSMIT_PDO_NOTIFY_FRYER_STARTUP
    NOTIFY_SHUTDOWN                     = 0x180b  # TPDO14 - L0_I_NOTIFY_SHUTDOWN
    NOTIFY_PREHEAT_START                = 0x1807  # TPDO10 - L0_I_NOTIFY_PREHEAT_START
    NOTIFY_PREHEAT_STOP                 = 0x180a  # TPDO13 - L0_I_NOTIFY_PREHEAT_STOP
    NOTIFY_PREHEAT_UPDATE               = 0x1808  # TPDO11 - L0_I_NOTIFY_PREHEAT_UPDATE
    NOTIFY_PREHEAT_COMPLETE             = 0x1809  # TPDO12 - L0_I_NOTIFY_PREHEAT_COMPLETE
    NOTIFY_COOK_START                   = 0x1803  # TPDO4  - L0_I_NOTIFY_COOK_TIMER_START_RECIEVED
    NOTIFY_COOK_STOP                    = 0x1804  # TPDO5  - L0_I_NOTIFY_COOK_TIMER_STOP
    NOTIFY_COOK_UPDATE                  = 0x1805  # TPDO6  - L0_I_NOTIFY_COOK_TIMER_UPDATE
    BOARD_STATUS                        = 0x1802  # TPDO3  - L0_I_CONTROL_BRD_STATUS (periodic)
    IO_STATS                            = 0x1800  # TPDO1  - L0_I_CONTROL_BRD_IO_STATS (periodic)
    RTC_DATE_TIME                       = 0x1801  # TPDO2  - L0_I_RTC_DATE_TIME (periodic)
    MODE_STATE                          = 0x2022  #        - L0_I_MODESTATE
    NOTIFY_ECO_MODE                     = 0x180e  # TPDO17 - L0_I_NOTIFY_ECO_MODE
    NOTIFY_RAPID_HEAT                   = 0x180f  # TPDO18 - L0_I_NOTIFY_RAPID_HEAT
    NOTIFY_HPUNIT_SETTINGS              = 0x182a  # TPDO43 - L0_I_NOTIFY_HPUNIT_SETTINGS
    NOTIFY_FILTER_PAUSE                 = 0x1811  #        - L0_I_NOTIFY_FILTER_PAUSE
    NOTIFY_FILTER_RESUME                = 0x1812  #        - L0_I_NOTIFY_FILTER_RESUME
    NOTIFY_FILTER_SKIP_STEP             = 0x1813  # TPDO26 - L0_I_NOTIFY_FILTER_SKIP_STEP
    NOTIFY_FILTER_FINISHED              = 0x1816  #        - L0_I_NOTIFY_FILTER_FINISHED
    NOTIFY_FILTER_STOP                  = 0x1817  #        - L0_I_NOTIFY_FILTER_STOP
    NOTIFY_EXPRESS_FILTER_ALERT         = 0x1818  #        - L0_I_NOTIFY_EXPRESS_FILTER_ALERT
    NOTIFY_EXPRESS_FILTER_LATER         = 0x1819  #        - L0_I_NOTIFY_EXPRESS_FILTER_LATER
    NOTIFY_EXPRESS_FILTER_READY         = 0x181a  #        - L0_I_NOTIFY_EXPRESS_FILTER_READY
    NOTIFY_EXPRESS_FILTER_STARTED       = 0x181b  #        - L0_I_NOTIFY_EXPRESS_FILTER_STARTED_VAT
    NOTIFY_EXPRESS_FILTER_STEP          = 0x181c  #        - L0_I_NOTIFY_EXPRESS_FILTER_STEP
    NOTIFY_DAILY_FILTER_ALERT           = 0x181d  #        - L0_I_NOTIFY_DAILY_FILTER_ALERT
    NOTIFY_DAILY_FILTER_LATER           = 0x181e  #        - L0_I_NOTIFY_DAILY_FILTER_LATER
    NOTIFY_DAILY_FILTER_READY           = 0x181f  #        - L0_I_NOTIFY_DAILY_FILTER_READY
    NOTIFY_DAILY_FILTER_STARTED         = 0x1820  #        - L0_I_NOTIFY_DAILY_FILTER_STARTED
    NOTIFY_DAILY_FILTER_STEP_UPDATE     = 0x1821  #        - L0_I_NOTIFY_DAILY_FILTER_STEP_UPDATE
    NOTIFY_VALVE_STATE                  = 0x1827  #        - L0_I_NOTIFY_VALVE_STATE
    NOTIFY_OIL_MGMT_TASK_START          = 0x1823  #        - L0_I_NOTIFY_START_OIL_MANAGEMENT_TASK
    NOTIFY_OIL_MGMT_TASK_END            = 0x1824  #        - L0_I_NOTIFY_END_OIL_MANAGEMENT_TASK
    NOTIFY_OIL_MGMT_STEP                = 0x182b  #        - L0_I_NOTIFY_OIL_MANAGEMENT_STEP
    NOTIFY_REAR_DISPOSE_COUNTDOWN       = 0x182c  #        - L0_I_NOTIFY_REAR_DISPOSE_COUNTDOWN
    NOTIFY_SHAKE_ALERT                  = 0x182d  #        - L0_I_NOTIFY_SHAKE_ALERT
    NOTIFY_FOOD_QUALITY_ALERT           = 0x182e  #        - L0_I_NOTIFY_FOOD_QUALITY_ALERT
    NOTIFY_ERRORS                       = 0x182f  #        - L0_I_NOTIFY_ERRORS
    NOTIFY_FILTER_PAD_ALERT             = 0x1833  #        - L0_I_NOTIFY_FILTER_PAD_ALERT
    NOTIFY_EXPORT_STARTED               = 0x1831  #        - L0_I_NOTIFY_EXPORT_STARTED
    NOTIFY_EXPORT_ENDED                 = 0x1832  #        - L0_I_NOTIFY_EXPORT_ENDED
    NOTIFY_EXPORT_PROGRESS              = 0x1835  #        - L0_I_NOTIFY_EXPORT_PROGRESS
    NOTIFY_EXPORT_CANCELLED             = 0x1834  #        - L0_I_NOTIFY_EXPORT_CANCELLED
    NOTIFY_START_WELL_WIZARD            = 0x1836  # TPDO55 - L0_I_NOTIFY_START_WELL_WIZARD
    NOTIFY_WELL_WIZARD_STATUS           = 0x1837  # TPDO56 - L0_I_NOTIFY_WELL_WIZARD_STATUS

# ===========================================================================
# Line 1 (FDCAN2) COB-ID constants (CB <-> OMS)
# ===========================================================================
class L1_OMS_COB:
    SELECTOR_VALVE_RESP                = 0x1400  # RPDO1  - OMS selector valve state
    FILTER_PUMP_RESP                   = 0x1401  # RPDO2  - OMS filter pump state
    DRAIN_VALVE_RESP                   = 0x1402  # RPDO3  - OMS drain valve state
    TOKEN_GRANT                        = 0x1403  # RPDO4  - OMS token grant response
    TOKEN_RELEASE_ACK                  = 0x1404  # RPDO5  - OMS token release ack
    DISPOSE_SWITCH                     = 0x1405  # RPDO6  - L1_I_DISPOSE_SWITCH
    VERSION_RESP                       = 0x1406  # RPDO7  - OMS version info response
    BULK                               = 0x1407  #        - L1_I_OMS_BULK
    USB_STATE                          = 0x1408  # RPDO9  - L1_I_USB_STATE
    BULK_TRANSFER_BUFFER               = 0x1409  # RPDO10 - L1_I_BULKTRANSFERBUFFER
    BOARD_STATUS                       = 0x140a  # RPDO11 - L1_I_OMS_BRD_STATUS (periodic)
    WELL_WIZARD_START_RESP             = 0x140b  # RPDO12 - OMS well wizard start response
    WELL_WIZARD_STATUS                 = 0x140c  # RPDO13 - OMS well wizard status
    BULK_TANK_FULL                     = 0x140d  # RPDO14 - L1_I_BULKTANKFULL
    BULK_24VAC_INPUT                   = 0x140e  # RPDO15 - L1_I_BULK_24VAC_INPUT
    SERIAL_NUMBER_ACK                  = 0x140f  #        - Serial number received ack
    FILTER_PUMP_DEAD_HEAD              = 0x1410  # RPDO17 - L1_I_FILTER_PUMP_DEAD_HEAD

class L1_CB_COB:
    SELECTOR_VALVE                      = 0x1800  # TPDO1  - L1_I_SELECTORVALVE
    DRAIN_VALVE                         = 0x1801  # TPDO2  - L1_I_DRAINVALVE
    FILTER_PUMP                         = 0x1802  # TPDO3  - L1_I_FILTERPUMP
    ATO_PUMP                            = 0x1803  # TPDO4  - L1_I_ATOPUMP
    TOKEN_REQUEST                       = 0x1804  # TPDO5  - L1_I_TOKEN (CB requests token)
    TOKEN_RELEASE                       = 0x1805  # TPDO6  - L1_I_REQUESTRELEASEFILTERING
    RTI_PUMP                            = 0x1806  # TPDO7  - L1_I_RTI_PUMP
    REQUEST_OMS_VERSION                 = 0x1807  # TPDO8  - L1_I_REQUEST_BOARD_VERSION_INFO (OMS)
    CBTOOMS_WELL_WIZARD_START           = 0x1808  # TPDO9  - L1_I_CBTOOMS_REQUEST_START_WELL_WIZARD
    BULK_EXPORT_TRANSFER                = 0x1809  # TPDO10 - L1_I_BULK_EXPORT_TRANSFER_INFO
    CBTOOMS_WELL_WIZARD_SET             = 0x180a  # TPDO11 - L1_I_CBTOOMS_REQUEST_WELL_WIZARD_SET
    SET_STRING                          = 0x180b  #        - L1_I_REQUEST_SET_STRING (serial number)


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
    return CanMessage(arbitration_id=L0_HMI_COB.REQUEST_BOARD_VERSION,
                      data=bytes(8),)


def encode_version_response(major: int, minor: int, patch: int) -> CanMessage:
    data = bytearray(8)
    data[0] = major
    data[1] = minor
    data[2] = patch
    return CanMessage(arbitration_id=L0_CB_COB.RECEIVED_BOARD_VERSION,
                      data=bytes(data),)


@dataclass
class L0_UiReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.UI_READY

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=bytes(8))


@dataclass
class L0_PreheatStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.PREHEAT_START
    product_id: int = 0
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IB", self.product_id, self.vat),)


@dataclass
class L0_PreheatStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.PREHEAT_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_CookTimerStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.COOK_TIMER_START
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_CookTimerStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.COOK_TIMER_STOP
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_CookTimerComplete:
    COB_ID: ClassVar[int] = L0_HMI_COB.COOK_TIMER_COMPLETE
    product_id: int = 0
    vat: int = 0
    timer: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBB", self.product_id, self.vat, self.timer),)


@dataclass
class L0_VatOnOff:
    COB_ID: ClassVar[int] = L0_HMI_COB.VAT_ON_OFF
    on: bool = True

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", 1 if self.on else 0),)


@dataclass
class L0_EcoMode:
    COB_ID: ClassVar[int] = L0_HMI_COB.ECO_MODE
    toggle: int = 1
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.toggle, self.vat),)


@dataclass
class L0_RapidHeat:
    COB_ID: ClassVar[int] = L0_HMI_COB.RAPID_HEAT
    toggle: int = 1
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.toggle, self.vat),)


@dataclass
class L0_FryerShutdown:
    COB_ID: ClassVar[int] = L0_HMI_COB.FRYER_SHUTDOWN
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FilterPause:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILTER_PAUSE
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FilterResume:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILTER_RESUME
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FilterSkipStep:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILTER_SKIP_STEP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FilterStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILTER_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FilterDialogResponse:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILTER_DIALOG_RESPONSE
    vat: int = 0
    dialog: int = 0
    yes_no: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BBB", self.vat, self.dialog, self.yes_no),)


@dataclass
class L0_ExpressFilterLater:
    COB_ID: ClassVar[int] = L0_HMI_COB.EXPRESS_FILTER_LATER
    vat: int = 0
    timer_ab: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.timer_ab),)


@dataclass
class L0_ExpressFilterReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.EXPRESS_FILTER_READY
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_ExpressFilterStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.EXPRESS_FILTER_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DailyFilterLater:
    COB_ID: ClassVar[int] = L0_HMI_COB.DAILY_FILTER_LATER
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DailyFilterReady:
    COB_ID: ClassVar[int] = L0_HMI_COB.DAILY_FILTER_READY
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DailyFilterStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.DAILY_FILTER_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FillSetSource:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILL_SET_SOURCE
    vat: int = 0
    fill_source: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.fill_source),)


@dataclass
class L0_FillStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILL_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_FillStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.FILL_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DrainToPanStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.DRAIN_TO_PAN_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DrainToPanStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.DRAIN_TO_PAN_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DisposeStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.DISPOSE_START
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_DisposeStop:
    COB_ID: ClassVar[int] = L0_HMI_COB.DISPOSE_STOP
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_OilMgmtTaskStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.OIL_MGMT_TASK_START
    vat: int = 0
    task: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.vat, self.task),)


@dataclass
class L0_OilMgmtTaskEnd:
    COB_ID: ClassVar[int] = L0_HMI_COB.OIL_MGMT_TASK_END
    vat: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.vat),)


@dataclass
class L0_ClearError:
    COB_ID: ClassVar[int] = L0_HMI_COB.CLEAR_ERROR
    error: int = 0
    action: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<HB", self.error, self.action),)


@dataclass
class L0_ProductNamesRequest:
    COB_ID: ClassVar[int] = L0_HMI_COB.PRODUCT_NAMES
    locale: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<H", self.locale),)


@dataclass
class L0_ProductDataRequest:
    COB_ID: ClassVar[int] = L0_HMI_COB.PRODUCT_DATA
    product_id: int = 0
    timer_set_in_secs: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<II", self.product_id, self.timer_set_in_secs),)


@dataclass
class L0_UpdateSettings:
    COB_ID: ClassVar[int] = L0_HMI_COB.UPDATE_SETTINGS

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=bytes(8),)


@dataclass
class L0_WellWizardStart:
    COB_ID: ClassVar[int] = L0_HMI_COB.START_WELL_WIZARD
    action: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.action),)


@dataclass
class L0_WellWizardSet:
    COB_ID: ClassVar[int] = L0_HMI_COB.WELL_WIZARD_SET
    id: int = 0
    screen: int = 0
    num: int = 0
    node_id: int = 0
    icon_state: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IBBBB", self.id, self.screen, self.num, self.node_id, self.icon_state),)


@dataclass
class L0_HmiBoardVersionInfo:
    COB_ID: ClassVar[int] = L0_HMI_COB.BOARD_VERSION_INFO
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
class L0_BackendReady:
    COB_ID: ClassVar[int] = L0_CB_COB.BACKEND_READY

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_BackendReady":
        return L0_BackendReady()


@dataclass(frozen=True)
class L0_PreheatStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_PREHEAT_START
    product_id: int
    vat_temp: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PreheatStarted":
        product_id, vat_temp, vat = struct.unpack_from("<IIB", msg.data)
        return L0_PreheatStarted(product_id=product_id, vat_temp=vat_temp, vat=vat)


@dataclass(frozen=True)
class L0_PreheatStopped:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_PREHEAT_STOP
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PreheatStopped":
        return L0_PreheatStopped(vat=msg.data[0])


@dataclass(frozen=True)
class L0_CookTimerStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_COOK_START
    product_id: int
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_CookTimerStarted":
        product_id, seconds, vat, timer = struct.unpack_from("<IIBB", msg.data)
        return L0_CookTimerStarted(product_id=product_id, seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_CookTimerStopped:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_COOK_STOP
    product_id: int
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_CookTimerStopped":
        product_id, seconds, vat, timer = struct.unpack_from("<IIBB", msg.data)
        return L0_CookTimerStopped(product_id=product_id, seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_PreheatUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_PREHEAT_UPDATE
    vat_temp: int
    progress: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PreheatUpdate":
        vat_temp, progress, vat = struct.unpack_from("<IBB", msg.data)
        return L0_PreheatUpdate(vat_temp=vat_temp, progress=progress, vat=vat)


@dataclass(frozen=True)
class L0_PreheatComplete:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_PREHEAT_COMPLETE
    vat_temp: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_PreheatComplete":
        vat_temp, vat = struct.unpack_from("<IB", msg.data)
        return L0_PreheatComplete(vat_temp=vat_temp, vat=vat)


@dataclass(frozen=True)
class L0_CookTimerUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_COOK_UPDATE
    product_id: int
    seconds: int
    vat: int
    timer: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_CookTimerUpdate":
        product_id, seconds, vat, timer, state = struct.unpack_from("<IIBBB", msg.data)
        return L0_CookTimerUpdate(product_id=product_id, seconds=seconds, vat=vat, timer=timer, state=state)


@dataclass(frozen=True)
class L0_FryerStartup:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FRYER_STARTUP

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_FryerStartup":
        return L0_FryerStartup()


@dataclass(frozen=True)
class L0_Shutdown:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_SHUTDOWN
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_Shutdown":
        return L0_Shutdown(vat=msg.data[0])


@dataclass(frozen=True)
class L0_BoardStatus:
    COB_ID: ClassVar[int] = L0_CB_COB.BOARD_STATUS
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
    def from_can(msg: CanMessage) -> "L0_BoardStatus":
        (
            vata_tc, vata_tt, vatb_tc, vatb_tt,
            b1_ct, b2_ct, b3_ct, b4_ct,
            sq_flags, cdf_flags,
            b1_qt, b2_qt, b3_qt, b4_qt,
            vata_modes, vatb_modes, vata_oil, vatb_oil, extra,
            err_num, err_vat, err_num_r, err_vat_r,
        ) = struct.unpack_from("<4H4h2B4h5BHBHB", msg.data)
        return L0_BoardStatus(
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
class L0_IoStats:
    COB_ID: ClassVar[int] = L0_CB_COB.IO_STATS
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
    def from_can(msg: CanMessage) -> "L0_IoStats":
        (
            active, line_v, line_c, v24vac_v, v24vac_c,
            rect24vac, v12, v5, v3_3, pcb, p1, p2,
            audio, sdcard, flash,
        ) = struct.unpack_from("<b11H3B", msg.data)
        return L0_IoStats(
            active=active, line_voltage=line_v, line_current=line_c,
            v24vac_voltage=v24vac_v, v24vac_current=v24vac_c,
            rectified_24vac=rect24vac, v12vdc=v12, v5vdc=v5, v3_3vdc=v3_3,
            pcb_temp=pcb, pressure1=p1, pressure2=p2,
            audio_flag=audio, sdcard_flag=sdcard, flash_flag=flash,
        )


@dataclass(frozen=True)
class L0_RtcDateTime:
    COB_ID: ClassVar[int] = L0_CB_COB.RTC_DATE_TIME
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
    def from_can(msg: CanMessage) -> "L0_RtcDateTime":
        weekday, month, date, year, hours, minutes, seconds, time_format, update_rtc_flag = (
            struct.unpack_from("<9B", msg.data)
        )
        return L0_RtcDateTime(
            weekday=weekday, month=month, date=date, year=year,
            hours=hours, minutes=minutes, seconds=seconds,
            time_format=time_format, update_rtc_flag=update_rtc_flag,
        )


@dataclass(frozen=True)
class L0_ModeState:
    COB_ID: ClassVar[int] = L0_CB_COB.MODE_STATE
    name_enum: int
    mode_type: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_ModeState":
        name_enum, mode_type = struct.unpack_from("<HH", msg.data)
        return L0_ModeState(name_enum=name_enum, mode_type=mode_type)


@dataclass(frozen=True)
class L0_NotifyEcoMode:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_ECO_MODE
    toggle: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyEcoMode":
        toggle, vat = struct.unpack_from("<BB", msg.data)
        return L0_NotifyEcoMode(toggle=toggle, vat=vat)


@dataclass(frozen=True)
class L0_NotifyRapidHeat:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_RAPID_HEAT
    toggle: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyRapidHeat":
        toggle, vat = struct.unpack_from("<BB", msg.data)
        return L0_NotifyRapidHeat(toggle=toggle, vat=vat)


@dataclass(frozen=True)
class L0_NotifyHpunitSettings:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_HPUNIT_SETTINGS
    raw: bytes = b""

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyHpunitSettings":
        return L0_NotifyHpunitSettings(raw=bytes(msg.data))


@dataclass(frozen=True)
class L0_NotifyFilterPause:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_PAUSE
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterPause":
        return L0_NotifyFilterPause(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyFilterResume:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_RESUME
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterResume":
        return L0_NotifyFilterResume(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyFilterSkipStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_SKIP_STEP
    vat: int
    step: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterSkipStep":
        vat, step = struct.unpack_from("<BB", msg.data)
        return L0_NotifyFilterSkipStep(vat=vat, step=step)


@dataclass(frozen=True)
class L0_NotifyFilterFinished:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_FINISHED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterFinished":
        return L0_NotifyFilterFinished(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyFilterStop:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_STOP
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterStop":
        return L0_NotifyFilterStop(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyExpressFilterAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPRESS_FILTER_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExpressFilterAlert":
        return L0_NotifyExpressFilterAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyExpressFilterLater:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPRESS_FILTER_LATER
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExpressFilterLater":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotifyExpressFilterLater(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotifyExpressFilterReady:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPRESS_FILTER_READY
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExpressFilterReady":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotifyExpressFilterReady(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotifyExpressFilterStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPRESS_FILTER_STARTED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExpressFilterStarted":
        return L0_NotifyExpressFilterStarted(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyExpressFilterStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPRESS_FILTER_STEP
    vat: int
    step: int
    step_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExpressFilterStep":
        vat, step, step_state = struct.unpack_from("<BBB", msg.data)
        return L0_NotifyExpressFilterStep(vat=vat, step=step, step_state=step_state)


@dataclass(frozen=True)
class L0_NotifyDailyFilterAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_DAILY_FILTER_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyDailyFilterAlert":
        return L0_NotifyDailyFilterAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyDailyFilterLater:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_DAILY_FILTER_LATER
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyDailyFilterLater":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotifyDailyFilterLater(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotifyDailyFilterReady:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_DAILY_FILTER_READY
    vat: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyDailyFilterReady":
        vat, ok = struct.unpack_from("<BB", msg.data)
        return L0_NotifyDailyFilterReady(vat=vat, ok=ok)


@dataclass(frozen=True)
class L0_NotifyDailyFilterStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_DAILY_FILTER_STARTED
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyDailyFilterStarted":
        return L0_NotifyDailyFilterStarted(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyDailyFilterStepUpdate:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_DAILY_FILTER_STEP_UPDATE
    vat: int
    step: int
    step_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyDailyFilterStepUpdate":
        vat, step, step_state = struct.unpack_from("<BBB", msg.data)
        return L0_NotifyDailyFilterStepUpdate(vat=vat, step=step, step_state=step_state)


@dataclass(frozen=True)
class L0_NotifyValveState:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_VALVE_STATE
    vat: int
    valve: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyValveState":
        vat, valve, state = struct.unpack_from("<BBB", msg.data)
        return L0_NotifyValveState(vat=vat, valve=valve, state=state)


@dataclass(frozen=True)
class L0_NotifyOilMgmtTaskStart:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_OIL_MGMT_TASK_START
    vat: int
    task: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyOilMgmtTaskStart":
        vat, task, ok = struct.unpack_from("<BBB", msg.data)
        return L0_NotifyOilMgmtTaskStart(vat=vat, task=task, ok=ok)


@dataclass(frozen=True)
class L0_NotifyOilMgmtTaskEnd:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_OIL_MGMT_TASK_END
    vat: int
    task: int
    ok: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyOilMgmtTaskEnd":
        vat, task, ok = struct.unpack_from("<BBB", msg.data)
        return L0_NotifyOilMgmtTaskEnd(vat=vat, task=task, ok=ok)


@dataclass(frozen=True)
class L0_NotifyOilMgmtStep:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_OIL_MGMT_STEP
    step: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyOilMgmtStep":
        step, vat = struct.unpack_from("<HB", msg.data)
        return L0_NotifyOilMgmtStep(step=step, vat=vat)


@dataclass(frozen=True)
class L0_NotifyRearDisposeCountdown:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_REAR_DISPOSE_COUNTDOWN
    seconds: int
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyRearDisposeCountdown":
        seconds, vat = struct.unpack_from("<IB", msg.data)
        return L0_NotifyRearDisposeCountdown(seconds=seconds, vat=vat)


@dataclass(frozen=True)
class L0_NotifyShakeAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_SHAKE_ALERT
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyShakeAlert":
        vat, timer = struct.unpack_from("<BB", msg.data)
        return L0_NotifyShakeAlert(vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotifyFoodQualityAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FOOD_QUALITY_ALERT
    seconds: int
    vat: int
    timer: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFoodQualityAlert":
        seconds, vat, timer = struct.unpack_from("<IBB", msg.data)
        return L0_NotifyFoodQualityAlert(seconds=seconds, vat=vat, timer=timer)


@dataclass(frozen=True)
class L0_NotifyErrors:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_ERRORS
    id_number: int
    vat: int
    state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyErrors":
        id_number, vat, state = struct.unpack_from("<IBB", msg.data)
        return L0_NotifyErrors(id_number=id_number, vat=vat, state=state)


@dataclass(frozen=True)
class L0_NotifyFilterPadAlert:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_FILTER_PAD_ALERT
    vat: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyFilterPadAlert":
        return L0_NotifyFilterPadAlert(vat=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyExportStarted:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPORT_STARTED

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExportStarted":
        return L0_NotifyExportStarted()


@dataclass(frozen=True)
class L0_NotifyExportEnded:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPORT_ENDED
    success: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExportEnded":
        return L0_NotifyExportEnded(success=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyExportProgress:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPORT_PROGRESS
    total: int
    done: int
    overall_pct: int
    curfile_pct: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExportProgress":
        total, done, overall_pct, curfile_pct = struct.unpack_from("<QQBB", msg.data)
        return L0_NotifyExportProgress(total=total, done=done, overall_pct=overall_pct, curfile_pct=curfile_pct)


@dataclass(frozen=True)
class L0_NotifyExportCancelled:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_EXPORT_CANCELLED

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyExportCancelled":
        return L0_NotifyExportCancelled()


@dataclass(frozen=True)
class L0_NotifyStartWellWizard:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_START_WELL_WIZARD
    action: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L0_NotifyStartWellWizard":
        return L0_NotifyStartWellWizard(action=msg.data[0])


@dataclass(frozen=True)
class L0_NotifyWellWizardStatus:
    COB_ID: ClassVar[int] = L0_CB_COB.NOTIFY_WELL_WIZARD_STATUS
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
    def from_can(msg: CanMessage) -> "L0_NotifyWellWizardStatus":
        (
            wid1, wid2, wid3, wid4,
            screen, well_count,
            wn1, wn2, wn3, wn4,
            nid1, nid2, nid3, nid4,
            is1, is2, is3, is4,
        ) = struct.unpack_from("<4I14B", msg.data)
        return L0_NotifyWellWizardStatus(
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
class L1_SelectorValveResponse:
    COB_ID: ClassVar[int] = L1_OMS_COB.SELECTOR_VALVE_RESP
    destination_reached: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.destination_reached),)


@dataclass
class L1_DrainValveResponse:
    COB_ID: ClassVar[int] = L1_OMS_COB.DRAIN_VALVE_RESP
    number: int = 0
    open: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BB", self.number, self.open),)


@dataclass
class L1_FilterPumpResponse:
    COB_ID: ClassVar[int] = L1_OMS_COB.FILTER_PUMP_RESP
    on: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.on),)


@dataclass
class L1_TokenGrant:
    COB_ID: ClassVar[int] = L1_OMS_COB.TOKEN_GRANT
    id_low: int = 0
    id_high: int = 0
    allowed: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIB", self.id_low, self.id_high, self.allowed),)


@dataclass
class L1_TokenReleaseAck:
    COB_ID: ClassVar[int] = L1_OMS_COB.TOKEN_RELEASE_ACK
    id_low: int = 0
    id_high: int = 0
    request: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIB", self.id_low, self.id_high, self.request),)


@dataclass
class L1_DisposeSwitchState:
    COB_ID: ClassVar[int] = L1_OMS_COB.DISPOSE_SWITCH
    open: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.open),)


@dataclass
class L1_UsbState:
    COB_ID: ClassVar[int] = L1_OMS_COB.USB_STATE
    usb_status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.usb_status),)


@dataclass
class L1_OmsVersionResp:
    COB_ID: ClassVar[int] = L1_OMS_COB.VERSION_RESP
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
class L1_OmsBulk:
    COB_ID: ClassVar[int] = L1_OMS_COB.BULK
    operation: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.operation),)


@dataclass
class L1_BulkTransferBuffer:
    COB_ID: ClassVar[int] = L1_OMS_COB.BULK_TRANSFER_BUFFER
    data1: int = 0
    data2: int = 0
    field1: int = 0
    field2: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<IIBB", self.data1, self.data2, self.field1, self.field2),)


@dataclass
class L1_OmsBoardStatus:
    COB_ID: ClassVar[int] = L1_OMS_COB.BOARD_STATUS
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
class L1_OmsWellWizardStartResp:
    COB_ID: ClassVar[int] = L1_OMS_COB.WELL_WIZARD_START_RESP
    action: int = 0
    chip_id: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<BI", self.action, self.chip_id),)


@dataclass
class L1_OmsWellWizardStatus:
    COB_ID: ClassVar[int] = L1_OMS_COB.WELL_WIZARD_STATUS
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
class L1_BulkTankFull:
    COB_ID: ClassVar[int] = L1_OMS_COB.BULK_TANK_FULL
    bulk_status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.bulk_status),)


@dataclass
class L1_Bulk24VacInput:
    COB_ID: ClassVar[int] = L1_OMS_COB.BULK_24VAC_INPUT
    status: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.status),)


@dataclass
class L1_SerialNumberAck:
    COB_ID: ClassVar[int] = L1_OMS_COB.SERIAL_NUMBER_ACK
    ack: int = 1

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.ack),)


@dataclass
class L1_FilterPumpDeadHead:
    COB_ID: ClassVar[int] = L1_OMS_COB.FILTER_PUMP_DEAD_HEAD
    detected: int = 0

    def encode(self) -> CanMessage:
        return CanMessage(arbitration_id=self.COB_ID,
                          data=struct.pack("<B", self.detected),)


# ===========================================================================
# Line 1 - CB -> HIL command decoders
# ===========================================================================

@dataclass(frozen=True)
class L1_SelectorValveCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.SELECTOR_VALVE
    port: int
    destination_reached: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_SelectorValveCmd":
        port, destination_reached, token_id = struct.unpack_from("<BBB", msg.data)
        return L1_SelectorValveCmd(port=port, destination_reached=destination_reached, token_id=token_id)


@dataclass(frozen=True)
class L1_DrainValveCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.DRAIN_VALVE
    valve_number: int
    open: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_DrainValveCmd":
        valve_number, open_, token_id = struct.unpack_from("<BBB", msg.data)
        return L1_DrainValveCmd(valve_number=valve_number, open=open_, token_id=token_id)


@dataclass(frozen=True)
class L1_FilterPumpCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.FILTER_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_FilterPumpCmd":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_FilterPumpCmd(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_TokenRequest:
    COB_ID: ClassVar[int] = L1_CB_COB.TOKEN_REQUEST
    id_low: int
    id_high: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_TokenRequest":
        id_low, id_high, token_id = struct.unpack_from("<IIB", msg.data)
        return L1_TokenRequest(id_low=id_low, id_high=id_high, token_id=token_id)


@dataclass(frozen=True)
class L1_TokenRelease:
    COB_ID: ClassVar[int] = L1_CB_COB.TOKEN_RELEASE
    token_id: int
    id_low: int
    id_high: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_TokenRelease":
        token_id, id_low, id_high = struct.unpack_from("<BII", msg.data)
        return L1_TokenRelease(token_id=token_id, id_low=id_low, id_high=id_high)


@dataclass(frozen=True)
class L1_AtoPumpCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.ATO_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_AtoPumpCmd":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_AtoPumpCmd(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_RtiPumpCmd:
    COB_ID: ClassVar[int] = L1_CB_COB.RTI_PUMP
    on: int
    token_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_RtiPumpCmd":
        on, token_id = struct.unpack_from("<BB", msg.data)
        return L1_RtiPumpCmd(on=on, token_id=token_id)


@dataclass(frozen=True)
class L1_RequestOmsVersion:
    COB_ID: ClassVar[int] = L1_CB_COB.REQUEST_OMS_VERSION
    trigger: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_RequestOmsVersion":
        return L1_RequestOmsVersion(trigger=msg.data[0] if msg.data else 0)


@dataclass(frozen=True)
class L1_CbToOmsWellWizardStart:
    COB_ID: ClassVar[int] = L1_CB_COB.CBTOOMS_WELL_WIZARD_START
    action: int
    chip_id: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CbToOmsWellWizardStart":
        action, chip_id = struct.unpack_from("<BI", msg.data)
        return L1_CbToOmsWellWizardStart(action=action, chip_id=chip_id)


@dataclass(frozen=True)
class L1_BulkExportTransfer:
    COB_ID: ClassVar[int] = L1_CB_COB.BULK_EXPORT_TRANSFER
    field1: int
    field2: int
    data1: int
    data2: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_BulkExportTransfer":
        field1, field2, data1, data2 = struct.unpack_from("<BBII", msg.data)
        return L1_BulkExportTransfer(field1=field1, field2=field2, data1=data1, data2=data2)


@dataclass(frozen=True)
class L1_CbToOmsWellWizardSet:
    COB_ID: ClassVar[int] = L1_CB_COB.CBTOOMS_WELL_WIZARD_SET
    id: int
    screen: int
    num: int
    node_id: int
    icon_state: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_CbToOmsWellWizardSet":
        id_, screen, num, node_id, icon_state = struct.unpack_from("<IBBBB", msg.data)
        return L1_CbToOmsWellWizardSet(id=id_, screen=screen, num=num, node_id=node_id, icon_state=icon_state)


@dataclass(frozen=True)
class L1_SetString:
    COB_ID: ClassVar[int] = L1_CB_COB.SET_STRING
    trigger: int

    @staticmethod
    def from_can(msg: CanMessage) -> "L1_SetString":
        return L1_SetString(trigger=msg.data[0] if msg.data else 0)
