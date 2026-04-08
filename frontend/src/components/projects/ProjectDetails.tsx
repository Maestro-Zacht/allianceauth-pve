import { useQuery } from "@tanstack/react-query";
import { Col, Row } from "react-bootstrap";
import { useParams } from "react-router";
import { getProjectDetails } from "../../api/api";
import Loading from "../Loading";
import ProjectInfo from "./ProjectInfo";
import ProjectContributions from "./ProjectContributions";
import NavBackButton from "../NavBackButton";




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
        <NavBackButton url={`/pve/r/`} />
        <Row>
            {isLoading ?
                <Col xs={12} className="text-center"><Loading /></Col>
                : <>
                    <h1 className="page-header text-center">{data!.name}</h1>
                    <ProjectInfo project={data!} />
                    <ProjectContributions projectId={projectIdNum} />

                </>}
        </Row>
    </>
}
