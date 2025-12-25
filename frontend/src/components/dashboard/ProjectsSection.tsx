import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getProjectList } from "../../api/api";
import type { components } from "../../api/Schema";
import { Badge, Card, Col, Nav, Row, Tab } from "react-bootstrap";
import TimeAgo from "react-timeago";
import DataTable from "../tables/DataTablesBase";
import Loading from "../Loading";

type projectType = components["schemas"]["FundingProjectSchema"];

interface ProjectPaneProps {
    projects: projectType[];
}

const columnsActive = [
    { data: 'name' },
    { data: 'created_at' },
    { data: 'estimated_total' },
    { data: 'goal' },
    { data: 'actual_percentage' },
];

function ActiveProjectsPane({ projects }: ProjectPaneProps) {
    const { t, i18n } = useTranslation();

    const renderCreatedAt = (data: string, type: string, _: any) => {
        switch (type) {
            case 'display':
                return <TimeAgo date={data} />;
            default:
                return data;
        }
    }

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language, { maximumFractionDigits: 2 });
    }

    const renderTotals = (data: number, type: string, row: projectType) => {
        let estimated_total: number = data;
        let actual_total: number = row.current_total;
        switch (type) {
            case 'display':
                return <>
                    {renderNumber(estimated_total)} ({renderNumber(actual_total)})
                </>;
            default:
                return [estimated_total, actual_total];
        }
    }

    const renderPercentage = (data: number, type: string, row: projectType) => {
        let actual_percentage: number = data;
        let estimated_percentage: number = data + row.estimated_missing_percentage;
        switch (type) {
            case 'display':
                return <>
                    {renderNumber(estimated_percentage)} % ({renderNumber(actual_percentage)} %)
                </>;
            default:
                return [estimated_percentage, actual_percentage];
        }
    }

    return <>
        <DataTable
            columns={columnsActive} data={projects}
            className="table table-aa"
            slots={{
                1: renderCreatedAt,
                2: renderTotals,
                3: renderNumber,
                4: renderPercentage,
            }}
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
                    <th>{t('name')}</th>
                    <th>{t('age')}</th>
                    <th>{t('projects.estimated_total_heading')}</th>
                    <th>{t('goal')}</th>
                    <th>{t('projects.completed_percentage_heading')}</th>
                </tr>
            </thead>
        </DataTable>
    </>
}

const columnsFinished = [
    { data: 'name' },
    { data: 'completed_at' },
    { data: 'number_of_participants' },
    { data: 'goal' },
    { data: 'current_total' },
];

function FinishedProjectsPane({ projects }: ProjectPaneProps) {
    const { t, i18n } = useTranslation();

    const renderNumber = (data: number) => {
        return data.toLocaleString(i18n.language, { maximumFractionDigits: 0 });
    }

    const renderCompletedIn = (data: string, _: string, row: projectType) => {
        let completed_at = new Date(data);
        let created_at = new Date(row.created_at);
        let diffInDays = Math.floor(
            (completed_at.getTime() - created_at.getTime()) /
            (1000 * 60 * 60 * 24)
        );
        return diffInDays;
    }

    return <>
        <DataTable
            columns={columnsFinished} data={projects}
            className="table table-aa"
            slots={{
                1: renderCompletedIn,
                3: renderNumber,
                4: renderNumber,
            }}
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
                    <th>{t('name')}</th>
                    <th>{t('completed_in_days')}</th>
                    <th>{t('participants')}</th>
                    <th>{t('goal')}</th>
                    <th>{t('actual_total')}</th>
                </tr>
            </thead>
        </DataTable>
    </>
}

export default function ProjectsSection() {
    const { t } = useTranslation();
    const { data, isLoading, error } = useQuery({
        queryKey: ['projects'],
        queryFn: getProjectList,
    });

    if (error) {
        console.error("Error fetching project list:", error);
        return <p>Error fetching project list.</p>
    }

    const projects = data || [];

    const openProjects = projects.filter((project: projectType) => project.is_active);
    const closedProjects = projects.filter((project: projectType) => !project.is_active);

    return <>
        <Row>
            <Col xs={12} className="my-3">
                <Card>
                    <Tab.Container defaultActiveKey="active">
                        <Card.Header>
                            <Nav variant="tabs">
                                <Nav.Item>
                                    <Nav.Link eventKey="active">
                                        {t("projects.activeTab")}
                                        {!isLoading && <Badge className="ms-1">{openProjects.length}</Badge>}
                                    </Nav.Link>
                                </Nav.Item>
                                <Nav.Item>
                                    <Nav.Link eventKey="finished">
                                        {t("projects.finishedTab")}
                                    </Nav.Link>
                                </Nav.Item>
                            </Nav>
                        </Card.Header>
                        <Card.Body>
                            <Tab.Content>
                                <Tab.Pane eventKey="active">
                                    {
                                        isLoading ?
                                            <Loading /> :
                                            <ActiveProjectsPane projects={openProjects} />
                                    }
                                </Tab.Pane>
                                <Tab.Pane eventKey="finished">
                                    {
                                        isLoading ?
                                            <Loading /> :
                                            <FinishedProjectsPane projects={closedProjects} />
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
