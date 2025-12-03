'use client';

import {
  Card,
  Text,
  Title,
  Stack,
  Group,
  Divider,
  Box,
  Badge,
  SimpleGrid,
  ThemeIcon,
  Tabs,
} from '@mantine/core';
import { LineChart } from '@mantine/charts';
import {
  IconSnowflake,
  IconTemperature,
  IconDroplet,
  IconWind,
  IconCloud,
} from '@tabler/icons-react';
import styles from './ForecastCard.module.css';

export interface ForecastDataPoint {
  source: string;
  forecastTime: string;
  validTime: string;
  tempHighF: number | null;
  tempLowF: number | null;
  snowAmountIn: number | null;
  precipAmountIn: number | null;
  precipProbPct: number | null;
  windSpeedMph: number | null;
  windDirectionDeg: number | null;
  windGustMph: number | null;
  conditionsText: string | null;
  iconCode: string | null;
}

export interface ResortForecastData {
  resortName: string;
  forecasts: ForecastDataPoint[];
}

export interface ForecastCardProps {
  forecast: ResortForecastData;
}

const getSourceColor = (source: string): string => {
  switch (source) {
    case 'NWS':
      return 'blue';
    case 'OPEN_METEO':
      return 'cyan';
    default:
      return 'gray';
  }
};

const getSourceLabel = (source: string): string => {
  switch (source) {
    case 'NWS':
      return 'National Weather Service';
    case 'OPEN_METEO':
      return 'Open-Meteo';
    default:
      return source;
  }
};

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const getCardinalDirection = (deg: number | null): string => {
  if (deg === null) return 'N/A';
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const index = Math.round(deg / 22.5) % 16;
  return directions[index];
};

interface StatBlockProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: React.ReactNode;
  color?: string;
}

function StatBlock({ icon, label, value, subValue, color = 'blue' }: StatBlockProps) {
  return (
    <Box
      style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: 8,
        padding: '12px 16px',
        border: '1px solid rgba(255, 255, 255, 0.06)',
      }}
    >
      <Group gap="sm" align="flex-start">
        <ThemeIcon size={32} variant="light" color={color} radius="md">
          {icon}
        </ThemeIcon>
        <Stack gap={2}>
          <Text size="xs" c="dimmed" tt="uppercase" fw={500}>
            {label}
          </Text>
          <Text size="lg" fw={700} c="white">
            {value}
          </Text>
          {subValue && (
            <Box>
              {subValue}
            </Box>
          )}
        </Stack>
      </Group>
    </Box>
  );
}

export function ForecastCard({ forecast }: ForecastCardProps) {
  const { resortName, forecasts } = forecast;

  // Group forecasts by source
  const forecastsBySource = forecasts.reduce((acc, f) => {
    if (!acc[f.source]) {
      acc[f.source] = [];
    }
    acc[f.source].push(f);
    return acc;
  }, {} as Record<string, ForecastDataPoint[]>);

  const sources = Object.keys(forecastsBySource);

  // Get next 7 days of forecasts, grouped by date
  const now = new Date();
  const next7Days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() + i);
    return date.toISOString().split('T')[0];
  });

  // Prepare chart data for temperature (overlay both sources)
  const prepareTempChartData = (source: string) => {
    const sourceForecasts = forecastsBySource[source] || [];
    return next7Days.map(date => {
      const dayForecast = sourceForecasts.find(f => f.validTime.startsWith(date));
      return {
        date: formatDate(date),
        high: dayForecast?.tempHighF ?? null,
        low: dayForecast?.tempLowF ?? null,
      };
    }).filter(d => d.high !== null || d.low !== null);
  };

  // Prepare chart data for snow (overlay both sources)
  const prepareSnowChartData = (source: string) => {
    const sourceForecasts = forecastsBySource[source] || [];
    return next7Days.map(date => {
      const dayForecast = sourceForecasts.find(f => f.validTime.startsWith(date));
      return {
        date: formatDate(date),
        snow: dayForecast?.snowAmountIn ?? null,
      };
    }).filter(d => d.snow !== null);
  };

  // Calculate summary stats from latest forecasts
  const latestForecasts = sources.map(source => {
    const sourceForecasts = forecastsBySource[source] || [];
    return sourceForecasts[0];
  }).filter(Boolean);

  const avgTempHigh = latestForecasts
    .map(f => f.tempHighF)
    .filter((t): t is number => t !== null)
    .reduce((a, b, _, arr) => a + b / arr.length, 0) || null;

  const avgTempLow = latestForecasts
    .map(f => f.tempLowF)
    .filter((t): t is number => t !== null)
    .reduce((a, b, _, arr) => a + b / arr.length, 0) || null;

  const totalSnow = latestForecasts
    .slice(0, 7)
    .map(f => f.snowAmountIn)
    .filter((s): s is number => s !== null)
    .reduce((a, b) => a + b, 0);

  const avgPrecipProb = latestForecasts
    .map(f => f.precipProbPct)
    .filter((p): p is number => p !== null)
    .reduce((a, b, _, arr) => a + b / arr.length, 0) || null;

  const avgWindSpeed = latestForecasts
    .map(f => f.windSpeedMph)
    .filter((w): w is number => w !== null)
    .reduce((a, b, _, arr) => a + b / arr.length, 0) || null;

  return (
    <Card
      radius="md"
      p="md"
      className={styles.card}
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      {/* Header */}
      <Group justify="space-between" align="flex-start" mb="md">
        <Box>
          <Title order={3} c="white" size="h4">
            {resortName} Forecast
          </Title>
          <Text size="xs" c="dimmed" mt={4}>
            {sources.length} forecast source{sources.length !== 1 ? 's' : ''}
          </Text>
        </Box>
        <Group gap="xs">
          {sources.map(source => (
            <Badge
              key={source}
              size="sm"
              variant="light"
              color={getSourceColor(source)}
            >
              {source}
            </Badge>
          ))}
        </Group>
      </Group>

      <Divider color="dark.4" mb="md" />

      {/* Summary Stats */}
      <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="sm" mb="md">
        <StatBlock
          icon={<IconTemperature size={18} />}
          label="Temperature"
          value={
            avgTempHigh !== null && avgTempLow !== null
              ? `${Math.round(avgTempHigh)}°/${Math.round(avgTempLow)}°F`
              : 'N/A'
          }
          subValue={<Text size="xs" c="dimmed">7-day forecast</Text>}
          color="orange"
        />
        <StatBlock
          icon={<IconSnowflake size={18} />}
          label="Snow Forecast"
          value={totalSnow > 0 ? `${totalSnow.toFixed(1)}"` : '0"'}
          subValue={<Text size="xs" c="dimmed">Next 7 days</Text>}
          color="cyan"
        />
        <StatBlock
          icon={<IconDroplet size={18} />}
          label="Precip Chance"
          value={avgPrecipProb !== null ? `${Math.round(avgPrecipProb)}%` : 'N/A'}
          subValue={<Text size="xs" c="dimmed">Average</Text>}
          color="blue"
        />
        <StatBlock
          icon={<IconWind size={18} />}
          label="Wind"
          value={avgWindSpeed !== null ? `${Math.round(avgWindSpeed)} mph` : 'N/A'}
          subValue={<Text size="xs" c="dimmed">Average</Text>}
          color="gray"
        />
      </SimpleGrid>

      {/* Forecast Details by Source */}
      <Tabs defaultValue={sources[0] || ''} mb="md">
        <Tabs.List>
          {sources.map(source => (
            <Tabs.Tab key={source} value={source}>
              {getSourceLabel(source)}
            </Tabs.Tab>
          ))}
        </Tabs.List>

        {sources.map(source => {
          const sourceForecasts = forecastsBySource[source] || [];
          const tempData = prepareTempChartData(source);
          const snowData = prepareSnowChartData(source);

          return (
            <Tabs.Panel key={source} value={source} pt="md">
              <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
                {/* Temperature Chart */}
                <Box
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 8,
                    padding: 16,
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <Text size="sm" c="dimmed" fw={500} mb="sm">
                    Temperature Forecast
                  </Text>
                  {tempData.length > 0 ? (
                    <LineChart
                      h={140}
                      data={tempData}
                      dataKey="date"
                      series={[
                        { name: 'high', color: 'red', label: 'High' },
                        { name: 'low', color: 'blue', label: 'Low' },
                      ]}
                      curveType="monotone"
                      withXAxis
                      withYAxis={false}
                      withDots
                      dotProps={{ r: 3 }}
                      withTooltip
                      strokeWidth={2}
                      gridProps={{ display: 'none' }}
                      xAxisProps={{
                        tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 10 },
                        tickLine: false,
                        axisLine: false,
                      }}
                    />
                  ) : (
                    <Text c="dimmed" size="sm" ta="center" py="lg">
                      No temperature data
                    </Text>
                  )}
                </Box>

                {/* Snow Forecast Chart */}
                <Box
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 8,
                    padding: 16,
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                  }}
                >
                  <Text size="sm" c="dimmed" fw={500} mb="sm">
                    Snow Forecast
                  </Text>
                  {snowData.length > 0 ? (
                    <LineChart
                      h={140}
                      data={snowData}
                      dataKey="date"
                      series={[{ name: 'snow', color: 'cyan', label: 'Snow (in)' }]}
                      curveType="monotone"
                      withXAxis
                      withYAxis={false}
                      withDots
                      dotProps={{ r: 3 }}
                      withTooltip
                      strokeWidth={2}
                      gridProps={{ display: 'none' }}
                      xAxisProps={{
                        tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 10 },
                        tickLine: false,
                        axisLine: false,
                      }}
                    />
                  ) : (
                    <Text c="dimmed" size="sm" ta="center" py="lg">
                      No snow forecast
                    </Text>
                  )}
                </Box>
              </SimpleGrid>

              {/* Daily Forecast List */}
              <Box mt="md">
                <Text size="sm" c="dimmed" fw={500} mb="sm">
                  Daily Forecast
                </Text>
                <Stack gap="xs">
                  {sourceForecasts.slice(0, 7).map((f, idx) => (
                    <Box
                      key={idx}
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        borderRadius: 6,
                        padding: '12px',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                      }}
                    >
                      <Group justify="space-between" align="center">
                        <Box>
                          <Text size="sm" fw={500} c="white">
                            {formatDate(f.validTime)}
                          </Text>
                          <Text size="xs" c="dimmed">
                            {f.conditionsText || 'N/A'}
                          </Text>
                        </Box>
                        <Group gap="md">
                          {f.tempHighF !== null && f.tempLowF !== null && (
                            <Text size="sm" c="white">
                              {Math.round(f.tempHighF)}°/{Math.round(f.tempLowF)}°F
                            </Text>
                          )}
                          {f.snowAmountIn !== null && f.snowAmountIn > 0 && (
                            <Badge size="sm" variant="light" color="cyan" leftSection={<IconSnowflake size={12} />}>
                              {f.snowAmountIn.toFixed(1)}"
                            </Badge>
                          )}
                          {f.precipProbPct !== null && (
                            <Badge size="sm" variant="light" color="blue" leftSection={<IconDroplet size={12} />}>
                              {f.precipProbPct}%
                            </Badge>
                          )}
                        </Group>
                      </Group>
                    </Box>
                  ))}
                </Stack>
              </Box>
            </Tabs.Panel>
          );
        })}
      </Tabs>
    </Card>
  );
}

