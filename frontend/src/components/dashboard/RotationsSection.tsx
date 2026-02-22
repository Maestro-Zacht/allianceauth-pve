import { useQuery } from "@tanstack/react-query";
import { Badge, Card, Col, Nav, Row, Tab } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getRotationList } from "../../api/api";
import type { components } from "../../api/Schema";
import Loading from "../Loading";
import DataTable from "../tables/DataTablesBase";
import TimeAgo from "react-timeago";
import { useNavigate } from "react-router";


type rotationType = components["schemas"]["RotationSchema"];

interface RotationPaneProps {
    rotations: rotationType[];
}

const columnsOpen = [
    { data: 'name' },
    { data: 'created_at' },
    { data: 'number_of_members' },
    { data: 'estimated_total' },
];

function OpenRotationPane({ rotations }: RotationPaneProps) {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();

    const renderRotationName = (data: string, type: string, row: rotationType) => {
        switch (type) {
            case 'display':
                return <a
                    href={`/pve/r/rotations/${row.id}/`}
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(`/pve/r/rotations/${row.id}/`);
                    }}
                >
                    {data}
                </a>
            default:
                return data;
        }
    }

    const renderAge = (data: string, type: string, _: any) => {
        switch (type) {
            case 'display':
                return <TimeAgo date={data} />;
            default:
                return data;
        }
    }

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language);
    }

    return <>
        <DataTable
            columns={columnsOpen} data={rotations}
            className="table table-aa"
            slots={{
                0: renderRotationName,
                1: renderAge,
                3: renderNumber,
            }}
            options={{
                pageLength: 50,
                columnDefs: [
                    {
                        targets: '_all',
                        className: 'dt-left',
                    }
                ],
                ordering: false,
            }}
        >
            <thead>
                <tr>
                    <th>{t('name')}</th>
                    <th>{t('age')}</th>
                    <th>{t('participants')}</th>
                    <th>{t('current_total')}</th>
                </tr>
            </thead>
        </DataTable>
    </>
}

const columnsClosed = [
    { data: 'name' },
    { data: 'closed_at' },
    { data: 'number_of_members' },
    { data: 'actual_total' },
];

function ClosedRotationPane({ rotations }: RotationPaneProps) {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();

    const renderRotationName = (data: string, type: string, row: rotationType) => {
        switch (type) {
            case 'display':
                return <a
                    href={`/pve/r/rotations/${row.id}/`}
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(`/pve/r/rotations/${row.id}/`);
                    }}
                >
                    {`${row.id} - ${data}`}
                </a>
            default:
                return data;
        }
    }

    const renderClosedOn = (data: string, type: string, _: any) => {
        switch (type) {
            case 'display':
                return <TimeAgo date={data} />;
            default:
                return data;
        }
    }

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language);
    }

    return <>
        <DataTable
            columns={columnsClosed} data={rotations}
            className="table table-aa"
            slots={{
                0: renderRotationName,
                1: renderClosedOn,
                3: renderNumber,
            }}
            options={{
                pageLength: 50,
                columnDefs: [
                    {
                        targets: '_all',
                        className: 'dt-left',
                    }
                ],
                order: [[1, 'desc']],
                ordering: false,
            }}
        >
            <thead>
                <tr>
                    <th>{t('name')}</th>
                    <th>{t('closed_on')}</th>
                    <th>{t('participants')}</th>
                    <th>{t('total')}</th>
                </tr>
            </thead>
        </DataTable>
    </>
}

export default function RotationsSection() {
    const { t } = useTranslation();
    const { data, isLoading, error } = useQuery({
        queryKey: ['rotations'],
        queryFn: getRotationList,
    });

    if (error) {
        console.error("Error loading rotation data:", error);
        return <p>Error loading rotation data.</p>
    }

    const rotations = data || [];

    const openRotations = rotations.filter(
        (rotation: rotationType) => !rotation.is_closed
    ).sort(
        (a: rotationType, b: rotationType) => b.priority - a.priority
    );
    const closedRotations = rotations.filter(
        (rotation: rotationType) => rotation.is_closed
    ).sort(
        (a: rotationType, b: rotationType) => {
            const dateA = new Date(a.closed_at!);
            const dateB = new Date(b.closed_at!);
            return dateB.getTime() - dateA.getTime();
        }
    );

    return <>
        <Row>
            <Col xs={12} className="my-3">
                <Card>
                    <Tab.Container defaultActiveKey="open">
                        <Card.Header>
                            <Nav variant="tabs">
                                <Nav.Item>
                                    <Nav.Link eventKey="open">
                                        {t("rotations.openTab")}
                                        {!isLoading && <Badge className="ms-1">{openRotations.length}</Badge>}
                                    </Nav.Link>
                                </Nav.Item>
                                <Nav.Item>
                                    <Nav.Link eventKey="closed">
                                        {t("rotations.closedTab")}
                                    </Nav.Link>
                                </Nav.Item>
                            </Nav>
                        </Card.Header>
                        <Card.Body>
                            <Tab.Content>
                                <Tab.Pane eventKey="open">
                                    {
                                        isLoading ?
                                            <Loading /> :
                                            <OpenRotationPane rotations={openRotations} />
                                    }
                                </Tab.Pane>
                                <Tab.Pane eventKey="closed">
                                    {
                                        isLoading ?
                                            <Loading /> :
                                            <ClosedRotationPane rotations={closedRotations} />
                                    }
                                </Tab.Pane>
                            </Tab.Content>
                        </Card.Body>
                    </Tab.Container>
                </Card>
            </Col>
        </Row>
    </>
}
