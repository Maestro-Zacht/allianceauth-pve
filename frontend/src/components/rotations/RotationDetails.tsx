import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { getRotation } from "../../api/api";
import Loading from "../Loading";
import type { components } from "../../api/Schema";
import { Card, Col, Container, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import TimeAgo from "react-timeago";
import RotationSummarySection from "./RotationSummarySection";
import RotationEntriesSection from "./RotationEntriesSection";

type rotationType = components["schemas"]["RotationSchema"];

interface RotationHeaderProps {
    rotation: rotationType;
}

interface SimpleStatCardProps {
    title: string;
    value: any;
}

function SimpleStatCard({ title, value }: SimpleStatCardProps) {
    return <>
        <Col>
            <Card className="text-center">
                <Card.Body>
                    <Card.Title>{title}</Card.Title>
                    <Card.Text>{value}</Card.Text>
                </Card.Body>
            </Card>
        </Col>
    </>
}

function RotationHeader({ rotation }: RotationHeaderProps) {
    const { t, i18n } = useTranslation();

    const localizedTaxRate = (rotation.tax_rate / 100).toLocaleString(
        i18n.language,
        { style: 'percent' }
    );

    return <>
        <h1 className="page-header text-center">{rotation.name}</h1>
        <Col xs={12} className="my-3">
            <Row xs={1} md={3} className="g-5">
                <SimpleStatCard
                    title={t("age")}
                    value={<TimeAgo date={rotation.created_at} />}
                />
                <SimpleStatCard
                    title={t("estimated_total")}
                    value={rotation.estimated_total.toLocaleString(i18n.language)}
                />
                <SimpleStatCard
                    title={t("tax_rate")}
                    value={localizedTaxRate}
                />
            </Row>
        </Col>
    </>
}

export default function RotationDetails() {
    const { rotationId } = useParams();
    const { data, isLoading, error } = useQuery({
        queryKey: ['rotation', rotationId],
        queryFn: () => getRotation(parseInt(rotationId!)),
    });

    if (error) {
        console.error("Error loading rotation data:", error);
        return <div>Error loading rotation data.</div>;
    }

    return <>
        <Container fluid>
            {isLoading ?
                <Row>
                    <Col xs={12} className="text-center">
                        <Loading />
                    </Col>
                </Row> :
                <Row>
                    <RotationHeader rotation={data!} />
                    <RotationSummarySection rotationId={data!.id} isClosed={data!.is_closed} />
                    <RotationEntriesSection rotationId={data!.id} />
                </Row>
            }
        </Container>
    </>
}
