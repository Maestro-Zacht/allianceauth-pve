import { Fragment, useId } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getRotation } from "../../../api/api";
import type { EntryFormErrors, ExtendedEntryFormSchema, ExtendedShareItem } from "../EntryTypes";
import "./ShareSectionStyles.css";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import CharacterWithPortrait from "../../utils/CharacterWithPortrait";
import { Alert, Button, Form } from "react-bootstrap";
import { usePermissions } from "../../../providers/PermissionsProvider";
import TooltipComponent from "../../utils/TooltipComponent";
import SiteRangesModal from "./SiteRangesModal";
import { lastPastSite } from "../siteRanges";

type ShareErrors = EntryFormErrors["shares"][string];

function shareErrorMessages(errors: ShareErrors): string[] {
    return [
        ...errors.character_id,
        ...errors.role_name,
        ...errors.sites_root,
        ...Object.values(errors.sites).flatMap(rangeErrors => [...rangeErrors.first, ...rangeErrors.last]),
    ];
}

interface ActiveRangeCellProps {
    share: ExtendedShareItem;
    errors: ShareErrors | undefined;
}

function ActiveRangeCell({ share, errors }: ActiveRangeCellProps) {
    const { t } = useTranslation();
    const tooltipId = useId();
    const { updateEntryData } = useEntryProcessor();
    const active = share.active_sites;

    if (active === null) {
        return <div className="d-flex justify-content-center">
            <TooltipComponent id={tooltipId} text={t("open_site_range")}>
                <Button
                    variant="success"
                    size="sm"
                    onClick={() => updateEntryData({ type: "open_active_range", characterId: share.character_id })}
                >
                    <i className="fa-solid fa-plus"></i>
                </Button>
            </TooltipComponent>
        </div>;
    }

    const minFirst = share.sites.length > 0 ? lastPastSite(share) + 2 : 1;
    const isInverted = active.first !== null && active.last !== null && active.last < active.first;
    const activeErrors = errors?.sites[share.sites.length];
    const isInvalid = activeErrors !== undefined && activeErrors.first.length + activeErrors.last.length > 0;

    const updateSite = (field: "first" | "last", value: string) => updateEntryData({
        type: "update_active_site",
        characterId: share.character_id,
        field,
        value: parseInt(value),
    });

    return <div className="d-flex justify-content-center align-items-center gap-1">
        <Form.Control
            type="number"
            min={minFirst}
            max={active.last ?? undefined}
            value={active.first ?? ""}
            isInvalid={isInvalid}
            onChange={(e) => updateSite("first", e.target.value)}
            style={{ width: "8ch" }}
        />
        <span>-</span>
        <Form.Control
            type="number"
            min={active.first ?? minFirst}
            value={active.last ?? ""}
            isInvalid={isInvalid}
            onChange={(e) => updateSite("last", e.target.value)}
            style={{ width: "8ch" }}
        />
        <TooltipComponent id={tooltipId} text={t("close_site_range")}>
            <span className="d-inline-block">
                <Button
                    variant="warning"
                    size="sm"
                    disabled={isInverted}
                    style={isInverted ? { pointerEvents: "none" } : undefined}
                    onClick={() => updateEntryData({ type: "close_active_range", characterId: share.character_id })}
                >
                    <i className="fa-solid fa-stop"></i>
                </Button>
            </span>
        </TooltipComponent>
    </div>;
}

interface SharesSectionProps {
    rotationId: number;
    shares: ExtendedEntryFormSchema['shares'];
    roles: ExtendedEntryFormSchema['roles'];
    errors_root: EntryFormErrors['shares_root'] | undefined | null;
    errors: EntryFormErrors['shares'] | undefined | null;
}

export default function SharesSection({ rotationId, shares, roles, errors_root, errors }: SharesSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();
    const permissions = usePermissions();
    const { data: rotation } = useQuery({
        queryKey: ['rotations', rotationId],
        queryFn: () => getRotation(rotationId),
    });
    const showMain = !permissions?.pve_only_mains;
    const showSetup = (rotation?.max_daily_setups ?? 0) > 0;
    const usersClassName = [!showMain && "only-mains", !showSetup && "no-setup"].filter(Boolean).join(" ") || undefined;

    return <>
        <div id="users" className={usersClassName}>
            {shares.length === 0 ?
                <span className="all-cols text-center">{t("no_character_yet")}</span> :
                <>
                    <div className="share-row">
                        {showMain && <span>{t("users_main_character")}</span>}
                        <span>{t("character")}</span>
                        <span className="text-center">{t("role")}</span>
                        {showSetup && <span className="text-center">{t("setup")}</span>}
                        <span className="text-center">{t("past_ranges")}</span>
                        <span className="text-center">{t("active_range")}</span>
                        <span className="text-center">{t("delete")}</span>
                    </div>

                    {shares.map((share, index) => {
                        const shareErrors = errors?.[index];
                        const errorMessages = shareErrors ? shareErrorMessages(shareErrors) : [];

                        return <Fragment key={share.character_id}>
                            <div className={share.active_sites === null ? "share-row" : "share-row bg-success bg-opacity-10 border-success"}>
                                {showMain && <span className="d-flex justify-content-start align-items-center">
                                    <CharacterWithPortrait
                                        character_name={share.main_character_name}
                                        portrait_url={share.main_character_portrait_url}
                                    />
                                </span>}
                                <span className="d-flex justify-content-start align-items-center">
                                    <CharacterWithPortrait
                                        character_name={share.character_name}
                                        portrait_url={share.portrait_url}
                                    />
                                </span>
                                <Form.Select
                                    value={share.role_name}
                                    onChange={(e) => updateEntryData({
                                        type: "change_share_role",
                                        characterId: share.character_id,
                                        newRoleName: e.target.value
                                    })}
                                >
                                    {roles.map((role) => <option key={role.name} value={role.name}>{role.name}</option>)}
                                </Form.Select>
                                {showSetup && <span
                                    className="text-center align-self-center"
                                    onClick={() => updateEntryData({
                                        type: "toggle_share_value",
                                        characterId: share.character_id,
                                        field: "helped_setup"
                                    })}
                                >
                                    {share.helped_setup ?
                                        <i className="fas fa-heart fa-heart-red"></i> :
                                        <i className="far fa-heart fa-heart-red"></i>
                                    }
                                </span>}
                                <div className="d-flex justify-content-center">
                                    <SiteRangesModal share={share} />
                                </div>
                                <ActiveRangeCell share={share} errors={shareErrors} />
                                <Button
                                    variant="danger"
                                    style={{ transform: 'scale(0.8)' }}
                                    onClick={() => {
                                        updateEntryData({
                                            type: 'delete_share',
                                            characterId: share.character_id
                                        });
                                    }}
                                >
                                    <i className="fa-solid fa-trash-can"></i>
                                </Button>
                            </div>
                            {errorMessages.length > 0 && <Alert variant="danger" className="all-cols mb-0" dismissible>
                                {errorMessages.map((error, errorIndex) => <div key={errorIndex}>{error}</div>)}
                            </Alert>}
                        </Fragment>;
                    })}
                </>
            }
        </div>
        {errors_root && errors_root.length > 0 && <Alert variant="danger" className="mt-3" dismissible>
            {errors_root.map((error, index) => <div key={index}>{error}</div>)}
        </Alert>}
    </>
}
