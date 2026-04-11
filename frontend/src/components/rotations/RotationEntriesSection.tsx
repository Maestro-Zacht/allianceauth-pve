import { Button, Card, Col, Image } from "react-bootstrap";
import DataTable from "../tables/DataTablesBase";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { getRotationEntries } from "../../api/api";
import type { components } from "../../api/Schema";
import { useEffect, useRef, useState } from "react";
import type { DataTableRef } from "datatables.net-react";
import { useNavigate } from "react-router";

interface RotationEntriesSectionProps {
    rotationId: number;
}

type characterType = components["schemas"]["EveCharacterSchema"];

export default function RotationEntriesSection({ rotationId }: RotationEntriesSectionProps) {
    const [imagesLoaded, setImagesLoaded] = useState(0);
    const { t, i18n } = useTranslation();
    const { data, isLoading, error } = useQuery({
        queryKey: ['rotation', rotationId, 'entries'],
        queryFn: () => getRotationEntries(rotationId)
    });
    const tableRef = useRef<DataTableRef>(null);
    const navigate = useNavigate();

    if (error) {
        console.error('Error loading entries:', error);
        return <p>Error loading entries.</p>
    }

    const entries = data || [];

    const columns = [
        { data: 'created_at', type: 'date' },
        { data: 'total_user_count' },
        { data: 'total_site_count' },
        { data: 'estimated_total_after_tax' },
        { data: 'estimated_total' },
        { data: 'created_by_character' },
    ];

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language);
    }

    const renderDate = (data: string, type: string, _: any) => {
        switch (type) {
            case 'display':
                return new Date(data).toLocaleDateString((i18n.language === 'en' || i18n.language === 'en-US') ? 'en-GB' : i18n.language, {
                    year: 'numeric',
                    month: 'numeric',
                    day: 'numeric',
                    hour: "numeric",
                    minute: "numeric",
                    hour12: false,
                    timeZone: 'UTC',
                    timeZoneName: "short",
                });
            default:
                return data;
        }
    }

    const renderCreatedBy = (data: characterType, type: string, _: any) => {
        switch (type) {
            case 'display':
                return <>
                    <Image
                        src={`${data.portrait_url}?size=32`}
                        alt={data.character_name}
                        rounded className="me-2"
                        width={32} height={32}
                        onLoad={() => setImagesLoaded((prev) => prev + 1)}
                    />
                    <span>{data.character_name}</span>
                </>
            case 'type':
                return 'html';
            default:
                return data.character_name;
        }
    }


    const renderButton = (_: any, type: string, row: any) => {
        switch (type) {
            case 'display':
                return <>
                    <Button
                        size="sm"
                        variant="outline-info"
                        href={`/pve/r/rotations/${rotationId}/entries/${row.id}/`}
                        onClick={(e) => {
                            e.preventDefault();
                            navigate(`/pve/r/rotations/${rotationId}/entries/${row.id}/`);
                        }}
                    >
                        <i className="fa-solid fa-magnifying-glass-dollar"></i>
                    </Button>
                </>
            case 'filter':
                return '';
            case 'type':
                return 'html';
            case 'sort':
                return '';
        }
    }

    useEffect(() => {
        if (imagesLoaded > 0 && imagesLoaded >= entries.length) {
            tableRef.current?.dt()?.columns.adjust();
        }
    }, [imagesLoaded, entries.length]);


    return <>
        <Col xs={12} className="my-3">
            <Card>
                <Card.Body>
                    {!isLoading && <>
                        <DataTable
                            columns={columns} data={entries}
                            className="table table-aa"
                            ref={tableRef}
                            slots={{
                                0: renderDate,
                                3: renderNumber,
                                4: renderNumber,
                                5: renderCreatedBy,
                                6: renderButton,
                            }}
                            options={{
                                pageLength: 50,
                                columnDefs: [
                                    {
                                        targets: '_all',
                                        className: 'dt-left',
                                    },
                                    {
                                        targets: [0, 1, 2, 3, 4, 6],
                                        searchable: false,
                                    }
                                ],
                                ordering: false,
                            }}
                        >
                            <thead>
                                <tr>
                                    <th>{t('date')}</th>
                                    <th>{t('user_count')}</th>
                                    <th>{t('share_count')}</th>
                                    <th>{t('total_after_tax')}</th>
                                    <th>{t('total')}</th>
                                    <th>{t('created_by')}</th>
                                    <th></th>
                                </tr>
                            </thead>
                        </DataTable>
                    </>}
                </Card.Body>
            </Card>
        </Col>
    </>
}
