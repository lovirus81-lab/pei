import { BaseEdge, EdgeProps, getSmoothStepPath } from 'reactflow';

export default function UtilityEdge({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    style = {},
    markerEnd,
}: EdgeProps) {
    const [edgePath] = getSmoothStepPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    return (
        <BaseEdge
            path={edgePath}
            markerEnd={markerEnd}
            style={{ ...style, strokeWidth: 1.5, stroke: '#000', strokeDasharray: '5,5' }}
        />
    );
}
