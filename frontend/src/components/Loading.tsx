import { Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export default function Loading() {
    const { t } = useTranslation();
    return (
        <Spinner role="status">
            <span className="visually-hidden">{t("loading")}</span>
        </Spinner>
    );
}