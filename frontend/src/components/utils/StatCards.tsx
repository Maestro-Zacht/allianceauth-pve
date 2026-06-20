import { Card, Col } from "react-bootstrap";

interface SimpleStatCardProps {
    title: string;
    value: any;
    align?: boolean;
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

export function GroupCard({ title, value, align = false }: SimpleStatCardProps) {
    return <>
        <Card className="text-center">
            <Card.Header>{title}</Card.Header>
            <Card.Body>
                {align ? <div className="d-flex align-items-center justify-content-center h-100">
                    <Card.Text>
                        {value}
                    </Card.Text>
                </div> : <Card.Text>
                    {value}
                </Card.Text>}
            </Card.Body>
        </Card>
    </>
}
