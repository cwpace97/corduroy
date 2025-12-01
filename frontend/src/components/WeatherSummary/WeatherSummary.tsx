'use client';

import { Stack, Text, Group, ThemeIcon, Tooltip, Box } from '@mantine/core';
import {
  IconSnowflake,
  IconTrendingUp,
  IconTrendingDown,
  IconMinus,
  IconSun,
  IconCloud,
  IconCloudSnow,
  IconCloudRain,
} from '@tabler/icons-react';

export interface WeatherTrend {
  snowDepthChangeIn: number;
  snowDepthTrend: string;
  tempAvgF: number | null;
  totalPrecipIn: number;
  latestSnowDepthIn: number | null;
  snowConditions: string;
}

export interface DailyData {
  date: string;
  tempMinF: number | null;
  tempMaxF: number | null;
  precipTotalIn: number | null;
}

export interface WeatherSummaryProps {
  trend: WeatherTrend | null;
  dailyData?: DailyData[];
  compact?: boolean;
}

const getConditionColor = (condition: string): string => {
  switch (condition) {
    case 'excellent':
      return 'teal';
    case 'good':
      return 'green';
    case 'fair':
      return 'yellow';
    case 'poor':
      return 'red';
    default:
      return 'gray';
  }
};

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'increasing':
      return <IconTrendingUp size={12} />;
    case 'decreasing':
      return <IconTrendingDown size={12} />;
    default:
      return <IconMinus size={12} />;
  }
};

const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'increasing':
      return 'teal';
    case 'decreasing':
      return 'red';
    default:
      return 'gray';
  }
};

// Get weather condition icon based on conditions and precip
const getConditionIcon = (condition: string, precipTotal: number, tempAvg: number | null) => {
  // If there's significant recent precipitation and it's cold enough, show snow
  if (precipTotal > 0.5 && (tempAvg === null || tempAvg < 35)) {
    return <IconCloudSnow size={20} />;
  }
  // If there's precipitation but warm, show rain
  if (precipTotal > 0.5) {
    return <IconCloudRain size={20} />;
  }
  // Based on snow conditions
  if (condition === 'excellent' || condition === 'good') {
    return <IconCloudSnow size={20} />;
  }
  if (condition === 'fair') {
    return <IconCloud size={20} />;
  }
  // Default to sun for poor/no snow conditions
  return <IconSun size={20} />;
};

export function WeatherSummary({ trend, dailyData, compact = false }: WeatherSummaryProps) {
  if (!trend) {
    return (
      <Stack align="center" gap={4}>
        <IconCloudSnow size={compact ? 24 : 32} style={{ color: 'var(--mantine-color-dark-3)' }} />
        <Text c="dimmed" size="xs">
          No data
        </Text>
      </Stack>
    );
  }

  const conditionColor = getConditionColor(trend.snowConditions);
  const trendColor = getTrendColor(trend.snowDepthTrend);

  // Get most recent daily data for high/low temps
  const latestDaily = dailyData && dailyData.length > 0 
    ? dailyData[dailyData.length - 1] 
    : null;

  if (compact) {
    return (
      <Tooltip
        label={
          <Stack gap={4}>
            <Text size="xs">Snow Depth: {trend.latestSnowDepthIn?.toFixed(0) ?? 'N/A'}"</Text>
            <Text size="xs">7-Day Change: {trend.snowDepthChangeIn > 0 ? '+' : ''}{trend.snowDepthChangeIn.toFixed(1)}"</Text>
            <Text size="xs">Temp: H: {latestDaily?.tempMaxF?.toFixed(0) ?? '—'}° L: {latestDaily?.tempMinF?.toFixed(0) ?? '—'}°</Text>
            <Text size="xs">7-Day Precip: {trend.totalPrecipIn.toFixed(1)}"</Text>
          </Stack>
        }
        withArrow
        position="bottom"
      >
        <Stack align="flex-start" gap={2} style={{ cursor: 'pointer', minWidth: 100 }}>
          {/* Row 1: Condition icon */}
          <Group gap={6} align="center">
            <ThemeIcon
              size={28}
              radius="xl"
              variant="light"
              color={conditionColor}
            >
              {getConditionIcon(trend.snowConditions, trend.totalPrecipIn, trend.tempAvgF)}
            </ThemeIcon>
            <Text size="xs" c="dimmed" fw={500}>
              {trend.snowConditions.charAt(0).toUpperCase() + trend.snowConditions.slice(1)}
            </Text>
          </Group>

          {/* Row 2: Snow depth with trend */}
          <Group gap={4} align="center">
            <IconSnowflake size={12} style={{ color: 'var(--mantine-color-cyan-5)' }} />
            <Text size="xs" c="white" fw={500}>
              {trend.latestSnowDepthIn?.toFixed(0) ?? '—'}"
            </Text>
            <ThemeIcon size={14} variant="subtle" color={trendColor}>
              {getTrendIcon(trend.snowDepthTrend)}
            </ThemeIcon>
          </Group>

          {/* Row 3: Temp high/low */}
          <Text size="xs" c="dimmed">
            H: {latestDaily?.tempMaxF?.toFixed(0) ?? '—'}° L: {latestDaily?.tempMinF?.toFixed(0) ?? '—'}°
          </Text>

          {/* Row 4: Precip total */}
          <Text size="xs" c="dimmed">
            Precip: {trend.totalPrecipIn.toFixed(1)}"
          </Text>
        </Stack>
      </Tooltip>
    );
  }

  // Non-compact version (not used currently but keeping for flexibility)
  return (
    <Stack align="center" gap={4}>
      <ThemeIcon
        size={40}
        radius="xl"
        variant="light"
        color={conditionColor}
      >
        {getConditionIcon(trend.snowConditions, trend.totalPrecipIn, trend.tempAvgF)}
      </ThemeIcon>
      <Group gap={4} align="center">
        <Text size="sm" fw={600} c={conditionColor}>
          {trend.latestSnowDepthIn?.toFixed(0) ?? '—'}"
        </Text>
        <ThemeIcon size={18} variant="subtle" color={trendColor}>
          {getTrendIcon(trend.snowDepthTrend)}
        </ThemeIcon>
      </Group>
      <Text size="xs" c="dimmed">
        H: {latestDaily?.tempMaxF?.toFixed(0) ?? '—'}° L: {latestDaily?.tempMinF?.toFixed(0) ?? '—'}°
      </Text>
      <Text size="xs" c="dimmed">
        Precip: {trend.totalPrecipIn.toFixed(1)}"
      </Text>
    </Stack>
  );
}
