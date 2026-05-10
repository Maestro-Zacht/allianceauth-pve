import { Card, Container, Row, Col } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

export default function ErrorPage({ errorCode, message }: { errorCode: number; message: string }) {
    const { t } = useTranslation();
    return (
        <Container className="d-flex vh-100">
            <Row className="justify-content-center w-100">
                <Col xs={12} md={6} lg={4}>
                    <Card className="shadow">
                        <Card.Body className="text-center">
                            <Card.Title as="h1">{t("error", { code: errorCode })}</Card.Title>
                            <Card.Text className="mb-4">{message}</Card.Text>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};
