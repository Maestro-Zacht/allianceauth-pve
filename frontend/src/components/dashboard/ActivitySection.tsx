import { useQuery } from "@tanstack/react-query";
import { Card, CardGroup, Col, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { getUserPastActivity } from "../../api/api";
import Loading from "../Loading";

const activityMonths = [
    1,
    3,
    6,
    12
];

function ActivityCard({ months }: { months: number }) {
    const { t } = useTranslation();
    const { data, isLoading, error } = useQuery({
        queryKey: ['activity', 'months', months],
        queryFn: () => getUserPastActivity(months),
    });

    if (error) {
        console.error("Error loading activity data:", error);
        return <p>Error loading activity data.</p>
    }

    const activityData = data || { helped_setups: 0, actual_total: 0, estimated_total: 0 };

    return (
        <Card className="text-center">
            <Card.Header>
                {t('monthNumber', { count: months })}
            </Card.Header>
            <Card.Body>
                {isLoading ?
                    <Loading /> :
                    <>
                        <Card.Text>{t('isk', { isk: activityData.actual_total, style: 'decimal', maximumFractionDigits: 0 })}</Card.Text>
                        <Card.Text>{t('setupNumber', { count: activityData.helped_setups })}</Card.Text>
                    </>
                }
            </Card.Body>
        </Card>
    )
}

export default function ActivitySection() {
    return (
        <Row>
            <Col xs={12} className="my-3">
                <CardGroup>
                    {activityMonths.map((months) => (
                        <ActivityCard key={months} months={months} />
                    ))}
                </CardGroup>
            </Col>
        </Row>
    )
}
