import { Fragment, useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import "./AddCharacterSectionStyles.css"
import { useMutation } from "@tanstack/react-query";
import { searchRatters } from "../../../api/api";
import type { ExtendedShareItem } from "../EntryTypes";
import CharacterWithPortrait from "../../CharacterWithPortrait";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import useDebounce from "../../../hooks/debounceHook";
import Loading from "../../Loading";

type RatterType = Omit<ExtendedShareItem,
    'helped_setup' | 'site_count' | 'role_name' | 'isPresent'
> & {
    tooltip: string;
    isMain: boolean;
};

interface AddCharactersSectionProps {
    addedCharacterIds: number[];
}

export default function AddCharactersSection({ addedCharacterIds }: AddCharactersSectionProps) {
    const { t } = useTranslation();
    const [searchText, setSearchText] = useState("");
    const [searchResults, setSearchResults] = useState<RatterType[]>([]);
    const { updateEntryData } = useEntryProcessor();
    const mutation = useMutation({
        mutationFn: (text?: string | undefined) => searchRatters(text, addedCharacterIds),
        onSuccess: (data) => {
            const results: RatterType[] = data.map(ratter => {
                const isMain = ratter.character.character_id === ratter.main_character.character_id;
                return {
                    character_id: ratter.character.character_id,
                    characterName: ratter.character.character_name,
                    portraitUrl: ratter.character.portrait_url,
                    mainCharacterName: ratter.main_character.character_name,
                    mainCharacterPortraitUrl: ratter.main_character.portrait_url,
                    isMain,
                    tooltip: isMain ? ratter.extra_chars.join(", ") : ratter.main_character.character_name,
                };
            });
            setSearchResults(results);
        },
        onError: (error) => {
            alert(error);
            setSearchResults([]);
        }
    });

    const debouncedSearch = useDebounce(searchText, 500);
    useEffect(() => mutation.mutate(debouncedSearch), [debouncedSearch, addedCharacterIds.length]);

    return <>
        <Form.Control
            placeholder={t("search")}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
        />
        <hr />
        <div id="search-results">
            {searchResults.length === 0 ?
                <span className="all-cols text-center">{t("no_results")}</span> :
                mutation.isPending ?
                    <span className="all-cols text-center"><Loading /></span> :
                    searchResults.map(result => <Fragment key={`search-result-${result.character_id}`}>
                        <CharacterWithPortrait
                            character_name={t(
                                result.isMain ? "main_character_name" : "alt_character_name",
                                { character_name: result.characterName }
                            )}
                            portrait_url={result.portraitUrl}
                            skip_margin
                            tooltip={result.tooltip}
                        />
                        <Button
                            variant="success"
                            onClick={() => {
                                updateEntryData({
                                    type: 'add_character',
                                    characterId: result.character_id,
                                    characterName: result.characterName,
                                    portraitUrl: result.portraitUrl,
                                    mainCharacterName: result.mainCharacterName,
                                    mainCharacterPortraitUrl: result.mainCharacterPortraitUrl,
                                });
                                setSearchResults(prev => prev.filter(r => r.character_id !== result.character_id));
                            }}
                        >
                            {t("add")}
                        </Button>
                    </Fragment>)}
        </div>
    </>
}
