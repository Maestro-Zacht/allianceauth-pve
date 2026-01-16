import { useQuery } from "@tanstack/react-query";
import { Card, Col, Image, Nav, Tab } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { components } from "../../api/Schema";
import { getRotationSummary } from "../../api/api";
import Loading from "../Loading";
import DataTable from "../tables/DataTablesBase";

type rotationSummaryRowType = components["schemas"]["RotationSummarySchema"];

interface RotationSummaryTableProps {
    rotationSummary: rotationSummaryRowType[];
    isClosed: boolean;
}

const summaryOpenColumns = [
    { data: 'character_name' },
    { data: 'helped_setups' },
    { data: 'estimated_total' },
];

const summaryClosedColumns = [
    { data: 'character_name' },
    { data: 'helped_setups' },
    { data: 'actual_total' },
    { data: 'estimated_total' },
];

function RotationSummaryTable({ rotationSummary, isClosed }: RotationSummaryTableProps) {
    const { t, i18n } = useTranslation();

    const columns = isClosed ?
        summaryClosedColumns :
        summaryOpenColumns;

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language);
    }

    const renderCharacterName = (data: string, type: string, row: rotationSummaryRowType) => {
        switch (type) {
            case 'display':
                return <>
                    <Image src={`${row.portrait_url}?size=32`} alt={data} rounded className="me-2" width={32} height={32} />
                    <span>{data}</span> {/*TODO: copy text*/}
                </>
            default:
                return data;
        }
    }

    let slots: Record<number, any> = {
        0: renderCharacterName,
        2: renderNumber,
    }

    if (isClosed) {
        slots[3] = renderNumber;
    }

    return <>
        <DataTable
            columns={columns} data={rotationSummary}
            className="table table-aa"
            slots={slots}
            options={{
                pageLength: 50,
                columnDefs: [
                    {
                        targets: '_all',
                        className: 'dt-left',
                    }
                ],
            }}
        >
            <thead>
                <tr>
                    <th>{t('character')}</th>
                    <th>{t('setups')}</th>
                    {
                        isClosed ?
                            <>
                                <th>{t('actual_total')}</th>
                                <th>{t('estimated_total')}</th>
                            </> :
                            <th>{t('total')}</th>
                    }
                </tr>
            </thead>
        </DataTable>
    </>
}

interface RotationSummarySectionProps {
    rotationId: number;
    isClosed: boolean;
}

// TODO: better summary + projects

export default function RotationSummarySection({ rotationId, isClosed }: RotationSummarySectionProps) {
    const { t } = useTranslation();
    const {
        data: summaryData,
        isLoading: summaryLoading,
        error: summaryError
    } = useQuery({
        queryKey: ["rotation", rotationId, "summary"],
        queryFn: () => getRotationSummary(rotationId),
    });

    if (summaryError) {
        console.error("Error loading rotation summary:", summaryError);
        return <p>Error loading rotation summary.</p>
    }

    const rotationSummary = summaryData || [];

    return <>
        <Col xs={12} className="my-3">
            <Card>
                <Tab.Container defaultActiveKey="summary">
                    <Card.Header>
                        <Nav variant="tabs">
                            <Nav.Item>
                                <Nav.Link eventKey="summary">
                                    {summaryLoading ?
                                        <Loading /> :
                                        t("summary")
                                    }
                                </Nav.Link>
                            </Nav.Item>
                        </Nav>
                    </Card.Header>
                    <Card.Body>
                        <Tab.Content>
                            <Tab.Pane eventKey="summary">
                                <RotationSummaryTable rotationSummary={rotationSummary} isClosed={isClosed} />
                            </Tab.Pane>
                        </Tab.Content>
                    </Card.Body>
                </Tab.Container>
            </Card>
        </Col>
    </>
}
