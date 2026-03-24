import { Button, Card, Col, Container, Form, Row } from "react-bootstrap";
import type { i18n, TFunction } from "i18next";
import { useTranslation } from "react-i18next";
import { z } from "zod";
import type { components, operations } from "../../api/Schema";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Loading from "../Loading";
import { useNavigate } from "react-router";
import { useToast } from "../../providers/ToastProvider";
import { useMutation } from "@tanstack/react-query";
import { createProject } from "../../api/api";
import { parseLocalizedNumber } from "../../utils";

type NewProjectType = components["schemas"]["NewProjectSchema"];
type NewProjectErrorType = operations["allianceauth_pve_api_projects_create_project"]["responses"][400]["content"]["application/json"];


const getNewProjectSchema = (t: TFunction<"translation", undefined>, i18n: i18n) => {
    return z.object({
        name: z.string()
            .min(1, { message: t("forms.min_len", { min: 1 }) })
            .max(128, { message: t("forms.max_len", { max: 128 }) }),
        goal: z.preprocess(
            (value) => {
                if (typeof value === "number") return value;
                if (typeof value === "string") return parseLocalizedNumber(value, i18n.language);
                return NaN;
            },
            z.number({ message: t("forms.number") }).int({ message: t("forms.integer") }).min(1, { message: t("forms.min_value", { min: 1 }) }),
        ),
    }) satisfies z.ZodType<NewProjectType>;
}

export default function NewProjectForm() {
    const { t, i18n } = useTranslation();
    const newProjectSchema = getNewProjectSchema(t, i18n);
    const {
        register,
        control,
        handleSubmit,
        setError,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(newProjectSchema),
    });
    const navigate = useNavigate();
    const addToast = useToast();
    const mutation = useMutation({
        mutationFn: createProject,
        onSuccess: (projectId) => {
            addToast(t("project_created"));
            navigate(`/pve/r/projects/${projectId}/`);
        },
        onError: (errors: NewProjectErrorType) => Object.entries(errors).forEach(([field, messages]) => {
            setError(field as keyof NewProjectType, { type: "server", message: messages.join(" - ") });
        })
    });

    const onSubmit = (data: NewProjectType) => {
        mutation.mutate(data);
    };

    return <>
        <Container fluid>
            <Row>
                <h1 className="page-header text-center">{t("new_funding_project")}</h1>
                <Col xs={12} className="mt-4">
                    <Card>
                        <Card.Body>
                            <Form onSubmit={handleSubmit(onSubmit)}>

                                <Form.Group className="mb-3" controlId="name">
                                    <Form.Label>{t("name")}</Form.Label>
                                    <Form.Control
                                        type="text" placeholder={t("name")}
                                        {...register("name")}
                                        isInvalid={!!errors.name}
                                    />
                                    <Form.Control.Feedback type="invalid">
                                        {errors.name?.message}
                                    </Form.Control.Feedback>
                                </Form.Group>

                                <Form.Group className="mb-3" controlId="goal">
                                    <Form.Label>{t("goal")}</Form.Label>
                                    <Controller
                                        control={control}
                                        name="goal"
                                        render={({ field: { onChange, value, ref, ...field } }) => (
                                            <Form.Control
                                                ref={ref}
                                                type="text"
                                                placeholder={t("goal")}
                                                value={value !== undefined ? value as string : ''}
                                                onChange={(e) => {
                                                    const rawTypedValue = e.target.value;
                                                    const rawNumber = parseLocalizedNumber(rawTypedValue, i18n.language);
                                                    if (isNaN(rawNumber)) {
                                                        onChange(rawTypedValue);
                                                    }
                                                    else {
                                                        const formattedValue = rawNumber.toLocaleString(i18n.language);
                                                        onChange(formattedValue);
                                                    }
                                                }}
                                                isInvalid={!!errors.goal}
                                                {...field}
                                            />
                                        )}
                                    />
                                    <Form.Control.Feedback type="invalid">
                                        {errors.goal?.message}
                                    </Form.Control.Feedback>
                                </Form.Group>

                                <div className="d-flex flex-row-reverse">
                                    <Button variant="primary" type="submit" disabled={mutation.isPending}>
                                        {mutation.isPending ? <Loading size="sm" /> : t("submit")}
                                    </Button>
                                </div>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    </>
}
