import { Container } from "react-bootstrap";
import ActivitySection from "./ActivitySection";
import { useTranslation } from "react-i18next";
import RotationsSection from "./RotationsSection";
import ProjectsSection from "./ProjectsSection";

export default function Dashboard() {
    const { t } = useTranslation();

    return (
        <>
            <Container fluid>
                <h1 className="page-header text-center">{t('dashboard.title')}</h1>
                <ActivitySection />
                <RotationsSection />
                <ProjectsSection />
            </Container>
        </>
    );
}
