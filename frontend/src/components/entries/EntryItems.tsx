import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getEntryItems } from "../../api/api";
import { Card, Col } from "react-bootstrap";
import Loading from "../Loading";
import ItemSummary from "../summary/ItemSummary";

interface EntryItemsProps {
    rotationId: number;
    entryId: number;
}

export default function EntryItems({ rotationId, entryId }: EntryItemsProps) {
    const { t } = useTranslation();
    const { data, error, isLoading } = useQuery({
        queryKey: [rotationId, entryId, "items"],
        queryFn: () => getEntryItems(rotationId, entryId),
    });

    if (error) {
        return <div>Error loading entry items.</div>;
    }

    const items = data || [];

    return <>
        <Col xs={12} className="my-3">
            <Card>
                <Card.Header className="text-center">{t('loot_items')}</Card.Header>
                <Card.Body>
                    {isLoading ?
                        <Loading /> :
                        items.length === 0 ?
                            <div className="text-center">{t('no_loot_items')}</div> :
                            <ItemSummary items={items} />
                    }
                </Card.Body>
            </Card>
        </Col>
    </>
}
