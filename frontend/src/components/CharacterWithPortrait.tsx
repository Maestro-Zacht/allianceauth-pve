import { Image } from "react-bootstrap";
import TooltipComponent from "./TooltipComponent";

interface CharacterWithPortraitProps {
    character_name: string;
    portrait_url: string;
    skip_margin?: boolean;
    tooltip?: string;
}

export default function CharacterWithPortrait({ character_name, portrait_url, skip_margin, tooltip }: CharacterWithPortraitProps) {
    return <>
        <Image
            src={`${portrait_url}?size=32`}
            alt={character_name}
            rounded className={skip_margin ? undefined : "me-2"}
            width={32} height={32}
        />
        {tooltip ?
            <TooltipComponent id={`tooltip-${character_name}`} text={tooltip}>
                <span>{character_name}</span>
            </TooltipComponent> :
            <span>{character_name}</span>
        }
    </>
}