import { Card, Col, Row, Form, Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { components, operations } from "../../api/Schema";
import { z } from "zod";
import type { TFunction } from "i18next";
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery } from "@tanstack/react-query";
import { createRotation, getPveButtons, getRoleSetups } from "../../api/api";
import Loading from "../Loading";
import { Link, useNavigate } from "react-router";
import { useToast } from "../../providers/ToastProvider";

type NewRotationType = components["schemas"]["NewRotationSchema"];
type PvebuttonType = components["schemas"]["PveButtonSchema"];
type RoleSetupType = components["schemas"]["BaseRoleSetupSchema"];
type NewRotationErrorType = operations["allianceauth_pve_api_rotations_create_rotation"]["responses"][400]["content"]["application/json"];

const getNewRotationSchema = (t: TFunction<"translation", undefined>, entryIds: number[], roleSetupIds: number[]) => {
    const entryIdsSet = new Set(entryIds);
    const roleSetupIdsSet = new Set(roleSetupIds);

    return z.object({
        name: z.string()
            .min(1, { message: t("forms.min_len", { min: 1 }) })
            .max(128, { message: t("forms.max_len", { max: 128 }) }),
        priority: z.number({ message: t("forms.number") }).int({ message: t("forms.integer") }),
        tax_rate: z.number({ message: t("forms.number") }).min(0, { message: t("forms.min_value", { min: 0 }) }).max(100, { message: t("forms.max_value", { max: 100 }) }),
        max_daily_setups: z.number({ message: t("forms.number") }).int({ message: t("forms.integer") }).min(0, { message: t("forms.min_value", { min: 0 }) }),
        min_people_share_setup: z.number({ message: t("forms.number") }).int({ message: t("forms.integer") }).min(0, { message: t("forms.min_value", { min: 0 }) }),
        entry_buttons: z.array(
            z.coerce.number({ message: t("forms.number") }).int({ message: t("forms.integer") })
                .refine(id => entryIdsSet.has(id), { message: t("forms.invalid_choice") })
        ),
        roles_setups: z.array(
            z.coerce.number({ message: t("forms.number") }).int({ message: t("forms.integer") })
                .refine(id => roleSetupIdsSet.has(id), { message: t("forms.invalid_choice") })
        ),
    }) satisfies z.ZodType<NewRotationType>;
}

interface RotationFormProps {
    pveButtons: PvebuttonType[];
    roleSetups: RoleSetupType[];
}

function RotationForm({ pveButtons, roleSetups }: RotationFormProps) {
    const { t } = useTranslation();
    const newRotationSchema = getNewRotationSchema(t, pveButtons.map(b => b.id), roleSetups.map(r => r.id));
    const {
        register,
        handleSubmit,
        setError,
        formState: { errors },
    } = useForm({
        defaultValues: {
            priority: 100,
            tax_rate: 0,
            max_daily_setups: 1,
            min_people_share_setup: 3,
        },
        resolver: zodResolver(newRotationSchema),
    });
    const navigate = useNavigate();
    const addToast = useToast();
    const mutation = useMutation({
        mutationFn: createRotation,
        onSuccess: (rotationId) => {
            addToast(t("rotation_created"));
            navigate(`/pve/r/rotations/${rotationId}/`);
        },
        onError: (errors: NewRotationErrorType) => Object.entries(errors).forEach(([field, messages]) => {
            setError(field as keyof NewRotationType, { type: "server", message: messages.join(" - ") });
        }),
    });

    const onSubmit = (data: NewRotationType) => {
        mutation.mutate(data);
    };

    return <>
        <Form onSubmit={handleSubmit(onSubmit)}>

            <Form.Group className="mb-3" controlId="rotationName">
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

            <Form.Group className="mb-3" controlId="rotationPriority">
                <Form.Label>{t("priority")}</Form.Label>
                <Form.Control
                    type="number" placeholder={t("priority")}
                    {...register("priority", { valueAsNumber: true })}
                    isInvalid={!!errors.priority}
                />
                <Form.Text muted>{t("forms.priority_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.priority?.message}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3" controlId="rotationTaxRate">
                <Form.Label>{t("tax_rate")}</Form.Label>
                <Form.Control
                    type="number" placeholder={t("tax_rate")}
                    {...register("tax_rate", { valueAsNumber: true })}
                    isInvalid={!!errors.tax_rate}
                />
                <Form.Text muted>{t("forms.tax_rate_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.tax_rate?.message}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3" controlId="rotationMaxDailySetups">
                <Form.Label>{t("max_daily_setups")}</Form.Label>
                <Form.Control
                    type="number" placeholder={t("max_daily_setups")}
                    {...register("max_daily_setups", { valueAsNumber: true })}
                    isInvalid={!!errors.max_daily_setups}
                />
                <Form.Text muted>{t("forms.max_daily_setups_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.max_daily_setups?.message}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3" controlId="rotationMinPeopleShareSetup">
                <Form.Label>{t("min_people_share_setup")}</Form.Label>
                <Form.Control
                    type="number" placeholder={t("min_people_share_setup")}
                    {...register("min_people_share_setup", { valueAsNumber: true })}
                    isInvalid={!!errors.min_people_share_setup}
                />
                <Form.Text muted>{t("forms.min_people_share_setup_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.min_people_share_setup?.message}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3" controlId="rotationEntryButtons">
                <Form.Label>{t("entry_buttons")}</Form.Label>
                <Form.Select multiple {...register("entry_buttons", { valueAsNumber: true })} isInvalid={!!errors.entry_buttons}>
                    {pveButtons.map(button => <option key={button.id} value={button.id}>{button.text}</option>)}
                </Form.Select>
                <Form.Text muted>{t("forms.entry_buttons_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.entry_buttons?.message}
                </Form.Control.Feedback>
            </Form.Group>

            <Form.Group className="mb-3" controlId="rotationRoleSetups">
                <Form.Label>{t("roles_setups")}</Form.Label>
                <Form.Select multiple {...register("roles_setups", { valueAsNumber: true })} isInvalid={!!errors.roles_setups}>
                    {roleSetups.map(setup => <option key={setup.id} value={setup.id}>{setup.name}</option>)}
                </Form.Select>
                <Form.Text muted>{t("forms.roles_setups_help")}</Form.Text>
                <Form.Control.Feedback type="invalid">
                    {errors.roles_setups?.message}
                </Form.Control.Feedback>
            </Form.Group>



            <div className="d-flex flex-row-reverse">
                <Button variant="primary" type="submit" disabled={mutation.isPending}>
                    {mutation.isPending ? <Loading size="sm" /> : t("submit")}
                </Button>
                <Link to="/pve/r/" className="btn btn-danger me-2">{t("cancel")}</Link>
            </div>
        </Form>
    </>
}


export default function NewRotationForm() {
    const { t } = useTranslation();
    const { data: pveButtonsData, error: pveButtonsError, isLoading: pveButtonsLoading } = useQuery({
        queryKey: ["pveButtons"],
        queryFn: getPveButtons,
    });
    const { data: roleSetupsData, error: roleSetupsError, isLoading: roleSetupsLoading } = useQuery({
        queryKey: ["roleSetups"],
        queryFn: getRoleSetups,
    });

    if (roleSetupsError || pveButtonsError) {
        return <div>Error loading data</div>;
    }

    return <>
        <Row>
            <h1 className="page-header text-center">{t("new_rotation")}</h1>
            <Col xs={12} className="mt-4">
                <Card>
                    <Card.Body>
                        {pveButtonsLoading || roleSetupsLoading ?
                            <div className="text-center"><Loading /></div> :
                            <RotationForm pveButtons={pveButtonsData!} roleSetups={roleSetupsData!} />
                        }
                    </Card.Body>
                </Card>
            </Col>
        </Row>
    </>
}
