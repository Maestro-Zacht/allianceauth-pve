import { useQuery } from "@tanstack/react-query";
import { Card, Col } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getProjectSummary } from "../../api/api";
import Loading from "../utils/Loading";
import SummaryTable from "../summary/SummaryTable";

interface ProjectContributionsProps {
    projectId: number;
}

export default function ProjectContributions({ projectId }: ProjectContributionsProps) {
    const { t } = useTranslation();
    const { data, error, isLoading } = useQuery({
        queryKey: ["project", projectId, "summary"],
        queryFn: () => getProjectSummary(projectId),
    });

    if (error) {
        console.error("Error fetching project summary:", error);
        return <p>Error loading project contributions.</p>;
    }

    const contributions = data || [];

    return <>
        <Col xs={12} className="mt-4">
            <Card>
                <Card.Header className="text-center">{t("contributors")}</Card.Header>
                <Card.Body>
                    {isLoading ?
                        <div className="text-center"><Loading /></div> :
                        <SummaryTable summary={contributions} isClosed={true} isProjectSummary={true} />}
                </Card.Body>
            </Card>
        </Col>
    </>
}
