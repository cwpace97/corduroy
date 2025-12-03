'use client';

import { Stack, Text, Group, ThemeIcon, Tooltip, Box, Badge } from '@mantine/core';
import {
  IconSnowflake,
  IconTrendingUp,
  IconTrendingDown,
  IconMinus,
  IconSun,
  IconCloud,
  IconCloudSnow,
  IconCloudRain,
  IconTemperature,
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
  snowfallTotalIn?: number | null;
}

export interface HistoricalWeatherData {
  date: string;
  tempMinF: number | null;
  tempMaxF: number | null;
  snowfallTotalIn: number | null;
}

export interface ForecastDataPoint {
  validTime: string;
  tempHighF: number | null;
  tempLowF: number | null;
  snowAmountIn: number | null;
}

export interface WeatherSummaryProps {
  trend: WeatherTrend | null;
  dailyData?: DailyData[];
  historicalWeather?: HistoricalWeatherData[];
  forecasts?: ForecastDataPoint[];
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

// Helper function to determine condition from snowfall amount
const getSnowfallCondition = (snowfallInches: number): 'poor' | 'fair' | 'good' | 'great' | 'epic' => {
  if (snowfallInches < 3) return 'poor';
  if (snowfallInches >= 3 && snowfallInches < 7) return 'fair';
  if (snowfallInches >= 7 && snowfallInches < 12) return 'good';
  if (snowfallInches >= 12 && snowfallInches < 20) return 'great';
  return 'epic';
};

const getSnowConditionColor = (condition: string): string => {
  switch (condition) {
    case 'epic':
      return '#1e40af'; // dark blue
    case 'great':
      return '#187855'; // dark green
    case 'good':
      return '#22c55e'; // green
    case 'fair':
      return '#eab308'; // yellow
    case 'poor':
      return '#ef4444'; // red
    default:
      return '#6b7280'; // gray
  }
};

const getSnowConditionLabel = (condition: string): string => {
  switch (condition) {
    case 'epic': return 'Epic';
    case 'great': return 'Great';
    case 'good': return 'Good';
    case 'fair': return 'Fair';
    case 'poor': return 'Poor';
    default: return 'N/A';
  }
};

const getDateKey = (dateStr: string): string => {
  return dateStr.split('T')[0].split(' ')[0];
};

export function WeatherSummary({ trend, dailyData, historicalWeather, forecasts, compact = false }: WeatherSummaryProps) {
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

  // Calculate 7-day historical snowfall
  const sevenDayHistoricalSnowfall = (historicalWeather ?? [])
    .filter(h => h.snowfallTotalIn !== null && h.snowfallTotalIn > 0)
    .reduce((sum, h) => sum + (h.snowfallTotalIn ?? 0), 0);

  // Process forecasts - merge by date and calculate 7-day forecast snow
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const sevenDaysFromNow = new Date(today);
  sevenDaysFromNow.setDate(today.getDate() + 7);

  // Get today's forecast high/low
  const todayDateKey = today.toISOString().split('T')[0];
  const forecastByDate = new Map<string, { high: number | null; low: number | null; snow: number | null }>();
  
  if (forecasts) {
    for (const f of forecasts) {
      const dateKey = getDateKey(f.validTime);
      const existing = forecastByDate.get(dateKey);
      if (!existing) {
        forecastByDate.set(dateKey, { high: f.tempHighF, low: f.tempLowF, snow: f.snowAmountIn });
      } else {
        if (existing.high === null && f.tempHighF !== null) existing.high = f.tempHighF;
        if (existing.low === null && f.tempLowF !== null) existing.low = f.tempLowF;
        if (existing.snow === null && f.snowAmountIn !== null) existing.snow = f.snowAmountIn;
        else if (f.snowAmountIn !== null) existing.snow = (existing.snow ?? 0) + f.snowAmountIn;
      }
    }
  }

  const todayForecast = forecastByDate.get(todayDateKey);
  const todayHigh = todayForecast?.high ?? latestDaily?.tempMaxF ?? null;
  const todayLow = todayForecast?.low ?? latestDaily?.tempMinF ?? null;

  // Calculate 7-day forecast snow
  const sevenDayForecastSnow = Array.from(forecastByDate.entries())
    .filter(([dateKey]) => {
      const forecastDate = new Date(dateKey + 'T00:00:00');
      return forecastDate >= today && forecastDate < sevenDaysFromNow;
    })
    .reduce((sum, [, data]) => sum + (data.snow ?? 0), 0);

  // Get conditions for 7-day totals
  const historical7Condition = getSnowfallCondition(sevenDayHistoricalSnowfall);
  const forecast7Condition = getSnowfallCondition(sevenDayForecastSnow);

  if (compact) {
    return (
      <Tooltip
        label={
          <Stack gap={4}>
            <Text size="sm">Current Temp: {trend.tempAvgF?.toFixed(0) ?? '—'}°F</Text>
            <Text size="sm">Today's High: {todayHigh?.toFixed(0) ?? '—'}°F</Text>
            <Text size="sm">Today's Low: {todayLow?.toFixed(0) ?? '—'}°F</Text>
            <Text size="sm">7-Day Snowfall: {sevenDayHistoricalSnowfall.toFixed(1)}"</Text>
            <Text size="sm">7-Day Forecast: {sevenDayForecastSnow.toFixed(1)}"</Text>
          </Stack>
        }
        withArrow
        position="bottom"
      >
        <Stack align="flex-start" gap={6} style={{ cursor: 'pointer', minWidth: 200 }}>
          {/* Row 1: Current temp */}
          <Group gap={8} align="center">
            <ThemeIcon size={28} variant="light" color="orange" radius="md">
              <IconTemperature size={16} />
            </ThemeIcon>
            <Text size="sm" c="white" fw={700}>
              {trend.tempAvgF?.toFixed(0) ?? '—'}°F
            </Text>
            <Text size="sm" c="dimmed">
              H: {todayHigh?.toFixed(0) ?? '—'}° L: {todayLow?.toFixed(0) ?? '—'}°
            </Text>
          </Group>

          {/* Row 2: 7-Day Snowfall with condition badge */}
          <Group gap={8} align="center">
            <ThemeIcon size={28} variant="light" color="blue" radius="md">
              <IconSnowflake size={16} />
            </ThemeIcon>
            <Text size="sm" c="white" fw={600}>
              {sevenDayHistoricalSnowfall.toFixed(1)}"
            </Text>
            <Badge
              size="sm"
              variant="filled"
              style={{
                backgroundColor: getSnowConditionColor(historical7Condition),
                padding: '4px 8px',
              }}
            >
              {getSnowConditionLabel(historical7Condition)}
            </Badge>
          </Group>

          {/* Row 3: 7-Day Forecast with condition badge */}
          <Group gap={8} align="center">
            <ThemeIcon size={28} variant="light" color="teal" radius="md">
              <IconCloudSnow size={16} />
            </ThemeIcon>
            <Text size="sm" c="white" fw={600}>
              {sevenDayForecastSnow.toFixed(1)}"
            </Text>
            <Badge
              size="sm"
              variant="filled"
              style={{
                backgroundColor: getSnowConditionColor(forecast7Condition),
                padding: '4px 8px',
              }}
            >
              {getSnowConditionLabel(forecast7Condition)}
            </Badge>
          </Group>
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
