import { Card, Col } from "react-bootstrap";

interface SimpleStatCardProps {
    title: string;
    value: any;
}

export function SimpleStatCard({ title, value }: SimpleStatCardProps) {
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

export function GroupCard({ title, value }: SimpleStatCardProps) {
    return <>
        <Card className="text-center">
            <Card.Header>{title}</Card.Header>
            <Card.Body>
                <Card.Text>{value}</Card.Text>
            </Card.Body>
        </Card>
    </>
}