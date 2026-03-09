import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Col, Container, Row } from "react-bootstrap";
import { useParams } from "react-router";
import { getProjectDetails, toggleProjectComplete } from "../../api/api";
import Loading from "../Loading";
import ProjectInfo from "./ProjectInfo";
import ProjectContributions from "./ProjectContributions";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useToast } from "../../providers/ToastProvider";


interface ToggleCompleteButtonProps {
    projectId: number;
    isActive: boolean;
}

function ToggleCompleteButton({ projectId, isActive }: ToggleCompleteButtonProps) {
    const { t } = useTranslation();
    const [loading, setLoading] = useState(false);
    const queryClient = useQueryClient();
    const addToast = useToast();

    const handleToggleComplete = async () => {
        setLoading(true);
        try {
            await toggleProjectComplete(projectId);
            await queryClient.invalidateQueries({ queryKey: ["project", projectId] });
        } catch (error) {
            addToast(error as string, "danger");
        } finally {
            setLoading(false);
        }
    }

    return <>
        <Col xs={12} className="mt-3">
            <div className="d-flex flex-row-reverse">
                <Button onClick={handleToggleComplete} variant="danger" disabled={loading}>
                    {loading ? <Loading size="sm" /> : isActive ? t("mark_as_completed") : t("reopen")}
                </Button>
            </div>
        </Col>
    </>
}

export default function ProjectDetails() {
    const { projectId } = useParams();
    const projectIdNum = Number(projectId);
    const { data, isLoading, error } = useQuery({
        queryKey: ["project", projectIdNum],
        queryFn: () => getProjectDetails(projectIdNum),
    });

    if (error) {
        console.error("Error fetching project details:", error);
        return <div>Error loading project details.</div>;
    }

    return <>
        <Container fluid>
            <Row>
                {isLoading ?
                    <Col xs={12} className="text-center"><Loading /></Col>
                    : <>
                        <h1 className="page-header text-center">{data!.name}</h1>
                        <ProjectInfo project={data!} />
                        <ProjectContributions projectId={projectIdNum} />
                        {data!.user_can_manage && <ToggleCompleteButton projectId={projectIdNum} isActive={data!.is_active} />}
                    </>}
            </Row>
        </Container>
    </>
}
