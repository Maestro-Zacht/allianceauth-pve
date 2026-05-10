import React from 'react'
import { OverlayTrigger, Tooltip } from 'react-bootstrap'

interface TooltipComponentProps {
    id: string;
    text: string;
    children: React.ReactElement;
}

export default function TooltipComponent({ id, children, text }: TooltipComponentProps) {
    return (
        <OverlayTrigger overlay={<Tooltip id={id}>{text}</Tooltip>}>
            {children}
        </OverlayTrigger>
    )
}