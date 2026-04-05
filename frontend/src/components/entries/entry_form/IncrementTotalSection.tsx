import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getRotationButtons } from "../../../api/api";
import { Button, Col, Row } from "react-bootstrap";
import Loading from "../../Loading";
import TooltipComponent from "../../TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";

interface IncrementTotalSectionProps {
    rotationId: number
}

export default function IncrementTotalSection({ rotationId }: IncrementTotalSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();
    const { isLoading, error, data } = useQuery({
        queryKey: ['rotation', rotationId, 'buttons'],
        queryFn: () => getRotationButtons(rotationId),
    });

    if (error) {
        return <div>Error loading buttons</div>
    }

    const buttons = data || [];

    return <>
        <Row>
            {isLoading ?
                <div className="text-center"><Loading /></div> :
                buttons.map(button => <Col key={button.id} xs={12} sm={6} lg={3} className="my-2">
                    <TooltipComponent
                        id={`increment-button-${button.id}`}
                        text={t("entry.button_tooltip", { increment: button.amount })}
                    >
                        <Button
                            variant="info" className="w-100"
                            onClick={() => updateEntryData({ type: 'increment_estimated_total', increment: button.amount })}
                        >
                            {button.text}
                        </Button>
                    </TooltipComponent>
                </Col>)
            }
        </Row>
        Custom Increment
    </>
}
