import { Image } from "react-bootstrap";

interface CharacterWithPortraitProps {
    character_name: string;
    portrait_url: string;
}

export default function CharacterWithPortrait({ character_name, portrait_url }: CharacterWithPortraitProps) {
    return <>
        <Image
            src={`${portrait_url}?size=32`}
            alt={character_name}
            rounded className="me-2"
            width={32} height={32}
        />
        <span>{character_name}</span>
    </>
}