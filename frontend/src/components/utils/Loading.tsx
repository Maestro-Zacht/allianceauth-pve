import { Spinner, type SpinnerProps } from "react-bootstrap";
import { useTranslation } from "react-i18next";

interface LoadingProps {
    size?: SpinnerProps["size"];
}

export default function Loading({ size }: LoadingProps) {
    const { t } = useTranslation();
    return (
        <Spinner role="status" size={size}>
            <span className="visually-hidden">{t("loading")}</span>
        </Spinner>
    );
}
