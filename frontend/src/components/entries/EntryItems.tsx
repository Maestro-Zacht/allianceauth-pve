import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getEntryItems } from "../../api/api";
import { Card, Col, Image, Row, Table } from "react-bootstrap";
import Loading from "../Loading";
import type { components } from "../../api/Schema";

type EntryItemType = components["schemas"]["ExtendedEntryItemSchema"]

interface ItemTableProps {
    items: EntryItemType[];
    showSalePrice: boolean;
}

function ItemTable({ items, showSalePrice }: ItemTableProps) {
    const { t, i18n } = useTranslation();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language);
    }

    return <>
        {items.length === 0 ?
            <div>{t('no_loot_items')}</div> :
            <Table className="table-aa">
                <thead>
                    <tr>
                        <th scope="col">{t('item')}</th>
                        <th scope="col">{t('quantity')}</th>
                        {showSalePrice && <th scope="col">{t('sale_price')}</th>}
                    </tr>
                </thead>
                <tbody>
                    {items.map((item, index) => (
                        <tr key={index}>
                            <td>
                                <Image
                                    src={`${item.icon_url}?size=32`}
                                    alt={item.name}
                                    rounded width={32} height={32}
                                    className="me-2"
                                />
                                {item.name}
                            </td>
                            <td>{localizeNumber(item.quantity)}</td>
                            {showSalePrice && <td>{t("isk", { isk: item.sale_price! })}</td>}
                        </tr>
                    ))}
                </tbody>
            </Table>
        }
    </>
}

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
    const halfItemCount = Math.ceil(items.length / 2);
    const firstHalfItems = items.slice(0, halfItemCount);
    const secondHalfItems = items.slice(halfItemCount);
    const showSalePrice = items.some(item => item.sale_price !== null);

    return <>
        <Col xs={12} className="my-3">
            <Card>
                <Card.Header className="text-center">{t('loot_items')}</Card.Header>
                <Card.Body>
                    {isLoading ?
                        <Loading /> :
                        <Row>
                            <Col md={6}>
                                <ItemTable items={firstHalfItems} showSalePrice={showSalePrice} />
                            </Col>
                            <Col md={6}>
                                <ItemTable items={secondHalfItems} showSalePrice={showSalePrice} />
                            </Col>
                        </Row>
                    }
                </Card.Body>
            </Card>
        </Col>
    </>
}
