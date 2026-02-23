import type { Node } from 'reactflow';
import { getTagPrefix } from '../constants/tagPrefix';

export function generateTag(equipmentClass: string, existingNodes: Node[]): string {
    const prefix = getTagPrefix(equipmentClass);
    let maxNumber = 100; // Start before 101

    for (const node of existingNodes) {
        const tag = node.data?.tag || node.data?.label;
        if (tag && typeof tag === 'string' && tag.startsWith(`${prefix}-`)) {
            const numPart = tag.substring(prefix.length + 1);
            const num = parseInt(numPart, 10);
            if (!isNaN(num) && num > maxNumber) {
                maxNumber = num;
            }
        }
    }

    const nextNumber = maxNumber + 1;
    return `${prefix}-${nextNumber}`;
}
