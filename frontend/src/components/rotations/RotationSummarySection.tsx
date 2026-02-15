import { useQuery } from "@tanstack/react-query";
import { Button, Card, Col, Image, Nav, Row, Tab, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { components } from "../../api/Schema";
import { getRotationProjectsSummaries, getRotationSummary } from "../../api/api";
import Loading from "../Loading";
import { useState } from "react";
import "./RotationSummaryStyles.css";
import TooltipComponent from "../TooltipComponent";
import { useToast } from "../../providers/ToastProvider";

type summaryRowType = components["schemas"]["SummarySchema"] & {
    helped_setups?: number;
};

interface RotationSummaryRowProps {
    row: summaryRowType;
    isClosed: boolean;
    isProjectSummary: boolean;
}

function RotationSummaryRow({ row, isClosed, isProjectSummary }: RotationSummaryRowProps) {
    const { i18n, t } = useTranslation();
    const [copied, setCopied] = useState(false);
    const addToast = useToast();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    const handleCopy = async (e: React.MouseEvent) => {
        const text = e.currentTarget.textContent;
        await navigator.clipboard.writeText(text);
        setCopied(true);
        addToast(t("copied_to_clipboard", { text }));
    }

    return <tr className={copied ? "copied" : undefined}>
        <td>
            <Image
                src={`${row.portrait_url}?size=32`}
                alt={row.character_name}
                rounded className="me-2"
                width={32} height={32}
            />
            <span className="copy-text" onClick={handleCopy}>{row.character_name}</span>
        </td>
        {!isProjectSummary && <td>{row.helped_setups}</td>}
        {
            isClosed ?
                <>
                    <td className="copy-text" onClick={handleCopy}>{localizeNumber(row.actual_total)}</td>
                    <td>{localizeNumber(row.estimated_total)}</td>
                    <td>
                        <TooltipComponent id={row.portrait_url} text={t("clear_copy")}>
                            <Button variant="secondary" size="sm" onClick={() => setCopied(false)}>
                                <i className="fa-solid fa-broom"></i>
                            </Button>
                        </TooltipComponent>
                    </td>
                </> :
                <td>{localizeNumber(row.estimated_total)}</td>
        }
    </tr>
}

interface RotationSummaryTableProps {
    rotationSummary: summaryRowType[];
    isClosed: boolean;
    isProjectSummary: boolean;
}

function RotationSummaryTable({ rotationSummary, isClosed, isProjectSummary }: RotationSummaryTableProps) {
    const { t } = useTranslation();

    return <>
        <Col xs={12} md={6}>
            <Table className="table-aa">
                <thead>
                    <tr>
                        <th>{t('character')}</th>
                        {!isProjectSummary && <th>{t('setups')}</th>}
                        {
                            isClosed ?
                                <>
                                    <th>{t('actual_total')}</th>
                                    <th>{t('estimated_total')}</th>
                                    <th></th>
                                </> :
                                <th>{t('total')}</th>
                        }
                    </tr>
                </thead>
                <tbody>
                    {rotationSummary.map((row, index) => (
                        <RotationSummaryRow key={index} row={row} isClosed={isClosed} isProjectSummary={isProjectSummary} />
                    ))}
                </tbody>
            </Table>
        </Col>
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

    const splitIndex = Math.ceil(rotationSummary.length / 2);
    const firstHalf = rotationSummary.slice(0, splitIndex);
    const secondHalf = rotationSummary.slice(splitIndex);

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
                                <Row>
                                    <RotationSummaryTable rotationSummary={firstHalf} isClosed={isClosed} isProjectSummary={false} />
                                    <RotationSummaryTable rotationSummary={secondHalf} isClosed={isClosed} isProjectSummary={false} />
                                </Row>
                            </Tab.Pane>
                            {projectSummaries.map((projectData) => {
                                const splitIndex = Math.ceil(projectData.summary.length / 2);
                                const firstHalf = projectData.summary.slice(0, splitIndex);
                                const secondHalf = projectData.summary.slice(splitIndex);
                                return (
                                    <Tab.Pane key={projectData.project.id} eventKey={`project-${projectData.project.id}`}>
                                        <div className="text-center">
                                            <h4 className="mb-3">
                                                {t("project_summary_for", { projectName: projectData.project.name })}
                                            </h4>
                                        </div>
                                        <Row>
                                            <RotationSummaryTable rotationSummary={firstHalf} isClosed={isClosed} isProjectSummary={true} />
                                            <RotationSummaryTable rotationSummary={secondHalf} isClosed={isClosed} isProjectSummary={true} />
                                        </Row>
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
