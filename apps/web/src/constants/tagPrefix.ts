export const TAG_PREFIX_MAP: Record<string, string> = {
    // Equipment
    'centrifugal_pump': 'P',
    'reciprocating_pump': 'P',
    'metering_pump': 'P',
    'vessel_vertical': 'V',
    'vessel_horizontal': 'V',
    'vessel': 'V',
    'heat_exchanger': 'E',
    'reactor': 'R',
    'tank': 'TK',
    'column': 'C',
    'compressor': 'K',
    'blower': 'K',
    'filter': 'F',
    'dryer': 'D',
    'mixer': 'M',
    'conveyor': 'CV',

    // Valves
    'gate_valve': 'XV',
    'globe_valve': 'XV',
    'check_valve': 'XV',
    'ball_valve': 'XV',
    'butterfly_valve': 'XV',
    'safety_valve': 'XV',
    'three_way_valve': 'XV',
    'needle_valve': 'XV',
    'control_valve': 'CV',

    // Instruments
    'field_mounted': 'I',
    'panel_mounted': 'I',
    'dcs_shared': 'I',
    'plc_mounted': 'I',
};

export function getTagPrefix(equipmentClass: string): string {
    return TAG_PREFIX_MAP[equipmentClass] || 'EQ';
}
