import BaseTimeAgo, { type Formatter, type Props } from "react-timeago";

interface TimeAgoProps {
    date: Props["date"];
}

export default function TimeAgo({ date }: TimeAgoProps) {
    const customFormatter: Formatter = (value, unit, suffix, epochMilliseconds, nextFormatter, now) => {
        if (unit === 'week' || unit === 'month' || unit === 'year') {
            const millisecondsInADay = 1000 * 60 * 60 * 24;
            const differenceInDays = Math.round(
                Math.abs(Date.now() - epochMilliseconds) / millisecondsInADay
            );
            return `${differenceInDays} days ${suffix}`;
        }
        return nextFormatter(value, unit, suffix, epochMilliseconds, nextFormatter, now);
    };
    return <BaseTimeAgo date={date} formatter={customFormatter} />
}
