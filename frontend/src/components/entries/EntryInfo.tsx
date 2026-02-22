import { CardGroup, Col } from "react-bootstrap";
import { GroupCard } from "../StatCards";
import { useTranslation } from "react-i18next";
import TimeAgo from "react-timeago";
import CharacterWithPortrait from "../CharacterWithPortrait";
import type { components } from "../../api/Schema";

type EntryType = components["schemas"]["EntryDetailsSchema"];

interface EntryInfoProps {
    entry: EntryType;
}

export default function EntryInfo({ entry }: EntryInfoProps) {
    const { t, i18n } = useTranslation();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    return <>
        <Col xs={12} className="my-3">
            <CardGroup>
                <GroupCard
                    title={t('created')}
                    value={<TimeAgo date={entry.created_at} />}
                />
                <GroupCard
                    title={t('number_of_users')}
                    value={entry.total_user_count}
                />
                {
                    entry.funding_project && (
                        <GroupCard
                            title={t('funding_project')}
                            value={`${entry.funding_project.name} (${entry.funding_percentage}%)`}
                        />
                    )
                }
                <GroupCard
                    title={t('total_after_tax')}
                    value={localizeNumber(entry.estimated_total_after_tax)}
                />
                <GroupCard
                    title={t('total')}
                    value={localizeNumber(entry.estimated_total)}
                />
                <GroupCard
                    title={t('created_by')}
                    value={<CharacterWithPortrait
                        character_name={entry.created_by_character.character_name}
                        portrait_url={entry.created_by_character.portrait_url}
                    />}
                />
            </CardGroup>
        </Col>
    </>
}
