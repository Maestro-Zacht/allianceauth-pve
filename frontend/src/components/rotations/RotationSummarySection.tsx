import { useQuery } from "@tanstack/react-query";
import { Card, Col, Nav, Tab } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getRotationProjectsSummaries, getRotationSummary } from "../../api/api";
import Loading from "../Loading";
import SummaryTable from "../summary/SummaryTable";

interface RotationSummarySectionProps {
    rotationId: number;
    isClosed: boolean;
}

// TODO: better summary

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
    const {
        data: projectSummariesData,
        isLoading: projectSummariesLoading,
        error: projectSummariesError
    } = useQuery({
        queryKey: ["rotation", rotationId, "project_summaries"],
        queryFn: () => getRotationProjectsSummaries(rotationId),
    });

    const error = summaryError || projectSummariesError;
    if (error) {
        console.error("Error loading rotation summaries:", error);
        return <p>Error loading rotation summaries.</p>
    }

    const rotationSummary = summaryData || [];
    const projectSummaries = projectSummariesData || [];

    return <>
        <Col xs={12} className="my-3">
            <Card>
                <Tab.Container defaultActiveKey="summary">
                    <Card.Header>
                        <Nav variant="tabs">
                            <Nav.Item>
                                <Nav.Link eventKey="summary" disabled={summaryLoading}>
                                    {summaryLoading ?
                                        <Loading /> :
                                        t("summary")
                                    }
                                </Nav.Link>
                            </Nav.Item>
                            {projectSummariesLoading ? (
                                <Nav.Item>
                                    <Nav.Link disabled>
                                        <Loading />
                                    </Nav.Link>
                                </Nav.Item>
                            ) : (
                                projectSummaries.map((projectData) => (
                                    <Nav.Item key={projectData.project.id}>
                                        <Nav.Link eventKey={`project-${projectData.project.id}`}>
                                            {projectData.project.name}
                                        </Nav.Link>
                                    </Nav.Item>
                                ))
                            )}
                        </Nav>
                    </Card.Header>
                    <Card.Body>
                        <Tab.Content>
                            <Tab.Pane eventKey="summary">
                                <SummaryTable summary={rotationSummary} isClosed={isClosed} isProjectSummary={false} />
                            </Tab.Pane>
                            {projectSummaries.map((projectData) => {
                                return (
                                    <Tab.Pane key={projectData.project.id} eventKey={`project-${projectData.project.id}`}>
                                        <div className="text-center">
                                            <h4 className="mb-3">
                                                {t("project_summary_for", { projectName: projectData.project.name })}
                                            </h4>
                                        </div>
                                        <SummaryTable summary={projectData.summary} isClosed={isClosed} isProjectSummary={true} />
                                    </Tab.Pane>
                                );
                            })}
                        </Tab.Content>
                    </Card.Body>
                </Tab.Container>
            </Card>
        </Col>
    </>
}
