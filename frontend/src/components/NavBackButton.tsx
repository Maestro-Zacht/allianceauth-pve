import { Nav } from "react-bootstrap";
import ReactDOM from "react-dom";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

const menuRoot = document.getElementById("nav-right");

interface NavBackButtonProps {
    url: string;
}

export default function NavBackButton({ url }: NavBackButtonProps) {
    const { t } = useTranslation();

    if (!menuRoot) {
        return <></>;
    }
    return ReactDOM.createPortal(
        <>
            <Nav.Item as="li">
                <Link to={url} className="btn btn-info">
                    <i className="fa-solid fa-arrow-left"></i>
                    <span className="ms-1">{t("back")}</span>
                </Link>
            </Nav.Item>
        </>,
        menuRoot
    )
}
