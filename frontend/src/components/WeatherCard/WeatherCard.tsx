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
} from '@mantine/core';
import { AreaChart, CompositeChart } from '@mantine/charts';
import {
  IconSnowflake,
  IconTemperature,
  IconDroplet,
  IconWind,
  IconTrendingUp,
  IconTrendingDown,
  IconMinus,
  IconMapPin,
} from '@tabler/icons-react';
import styles from './WeatherCard.module.css';

export interface StationInfo {
  stationName: string;
  stationTriplet: string;
  distanceMiles: number;
}

export interface StationDailyData {
  stationName: string;
  stationTriplet: string;
  distanceMiles: number;
  snowDepthAvgIn: number | null;
}

export interface DailyWeatherData {
  date: string;
  snowDepthAvgIn: number | null;
  snowDepthMaxIn: number | null;
  tempMinF: number | null;
  tempMaxF: number | null;
  precipTotalIn: number | null;
  windSpeedAvgMph: number | null;
  windDirectionAvgDeg: number | null;
  stationData: StationDailyData[];
}

export interface HourlyWeatherData {
  date: string;
  hour: number | null;
  snowDepthIn: number | null;
  tempObservedF: number | null;
  precipAccumIn: number | null;
  windSpeedAvgMph: number | null;
}

export interface WeatherTrend {
  snowDepthChangeIn: number;
  snowDepthTrend: string;
  tempAvgF: number | null;
  totalPrecipIn: number;
  latestSnowDepthIn: number | null;
  snowConditions: string;
}

export interface ResortWeatherData {
  resortName: string;
  stations: StationInfo[];
  trend: WeatherTrend;
  dailyData: DailyWeatherData[];
  hourlyData: HourlyWeatherData[];
}

export interface WeatherCardProps {
  weather: ResortWeatherData;
}

// Single gray color for all station dashed lines
const STATION_LINE_COLOR = '#6b7280';

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

const getConditionLabel = (condition: string): string => {
  switch (condition) {
    case 'excellent':
      return 'Excellent';
    case 'good':
      return 'Good';
    case 'fair':
      return 'Fair';
    case 'poor':
      return 'Poor';
    default:
      return 'N/A';
  }
};

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'increasing':
      return <IconTrendingUp size={16} />;
    case 'decreasing':
      return <IconTrendingDown size={16} />;
    default:
      return <IconMinus size={16} />;
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

export function WeatherCard({ weather }: WeatherCardProps) {
  const { trend, dailyData, stations } = weather;
  const conditionColor = getConditionColor(trend.snowConditions);
  const trendColor = getTrendColor(trend.snowDepthTrend);

  // Get unique station triplets from the data
  const stationTriplets = stations.map(s => s.stationTriplet);
  
  // Create a map of triplet to station info for quick lookup
  const stationMap = new Map(stations.map(s => [s.stationTriplet, s]));

  // Prepare chart data for snow depth with individual station lines
  const snowChartData = dailyData.map(d => {
    const dataPoint: Record<string, string | number> = {
      date: d.date.slice(5), // MM-DD format
      weighted: d.snowDepthAvgIn ?? 0, // Weighted average (solid line)
    };
    
    // Add each station's snow depth
    d.stationData?.forEach(sd => {
      if (sd.snowDepthAvgIn !== null) {
        dataPoint[sd.stationTriplet] = sd.snowDepthAvgIn;
      }
    });
    
    return dataPoint;
  }).filter(d => d.weighted !== 0 || stationTriplets.some(t => d[t] !== undefined));

  // Build series for the snow chart - station lines as thin dashed gray lines
  const stationLineSeries = stationTriplets.map((triplet) => ({
    name: triplet,
    color: STATION_LINE_COLOR,
    strokeDasharray: '4 4',
    type: 'line' as const,
  }));

  // Weighted average as area chart
  const weightedAreaSeries = {
    name: 'weighted',
    color: 'cyan',
    type: 'area' as const,
  };

  // Prepare chart data for temperature (weighted averages only)
  const tempChartData = dailyData
    .filter(d => d.tempMinF !== null || d.tempMaxF !== null)
    .map(d => ({
      date: d.date.slice(5),
      min: d.tempMinF ?? 0,
      max: d.tempMaxF ?? 0,
    }));

  // Calculate min/max temps for the period
  const temps = dailyData.flatMap(d => [d.tempMinF, d.tempMaxF]).filter((t): t is number => t !== null);
  const minTemp = temps.length > 0 ? Math.min(...temps) : null;
  const maxTemp = temps.length > 0 ? Math.max(...temps) : null;

  // Calculate average wind speed and direction over the period
  const windSpeeds = dailyData.map(d => d.windSpeedAvgMph).filter((w): w is number => w !== null);
  const avgWindSpeed = windSpeeds.length > 0 ? windSpeeds.reduce((a, b) => a + b, 0) / windSpeeds.length : null;
  const windDirs = dailyData.map(d => d.windDirectionAvgDeg).filter((w): w is number => w !== null);
  const avgWindDir = windDirs.length > 0 ? Math.round(windDirs.reduce((a, b) => a + b, 0) / windDirs.length) : null;

  // Convert degrees to cardinal direction
  const getCardinalDirection = (deg: number): string => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(deg / 22.5) % 16;
    return directions[index];
  };

  // Get closest station for display
  const closestStation = stations[0];

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
            {weather.resortName}
          </Title>
          <Group gap={4} mt={4}>
            <IconMapPin size={12} style={{ color: 'var(--mantine-color-dimmed)' }} />
            <Text size="xs" c="dimmed">
              {stations.length} SNOTEL stations ({closestStation?.distanceMiles.toFixed(1)} - {stations[stations.length - 1]?.distanceMiles.toFixed(1)} mi)
            </Text>
          </Group>
        </Box>
        <Badge
          size="lg"
          variant="light"
          color={conditionColor}
          leftSection={<IconSnowflake size={14} />}
        >
          {getConditionLabel(trend.snowConditions)}
        </Badge>
      </Group>

      <Divider color="dark.4" mb="md" />

      {/* Stats Grid */}
      <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="sm" mb="md">
        <StatBlock
          icon={<IconSnowflake size={18} />}
          label="Snow Depth"
          value={trend.latestSnowDepthIn !== null ? `${trend.latestSnowDepthIn.toFixed(0)}"` : 'N/A'}
          subValue={
            <Group gap={4}>
              <ThemeIcon size={14} variant="subtle" color={trendColor}>
                {getTrendIcon(trend.snowDepthTrend)}
              </ThemeIcon>
              <Text size="xs" c={trendColor}>
                {trend.snowDepthChangeIn > 0 ? '+' : ''}{trend.snowDepthChangeIn.toFixed(1)}" 7d
              </Text>
            </Group>
          }
          color="cyan"
        />
        <StatBlock
          icon={<IconTemperature size={18} />}
          label="Temperature"
          value={trend.tempAvgF !== null ? `${trend.tempAvgF.toFixed(0)}°F` : 'N/A'}
          subValue={
            minTemp !== null && maxTemp !== null ? (
              <Text size="xs" c="dimmed">{minTemp.toFixed(0)}° - {maxTemp.toFixed(0)}°</Text>
            ) : undefined
          }
          color="orange"
        />
        <StatBlock
          icon={<IconDroplet size={18} />}
          label="Precipitation"
          value={`${trend.totalPrecipIn.toFixed(1)}"`}
          subValue={<Text size="xs" c="dimmed">7-day total</Text>}
          color="blue"
        />
        <StatBlock
          icon={<IconWind size={18} />}
          label="Avg Wind"
          value={avgWindSpeed !== null ? `${avgWindSpeed.toFixed(0)} mph` : 'N/A'}
          subValue={
            avgWindDir !== null ? (
              <Text size="xs" c="dimmed">{getCardinalDirection(avgWindDir)} ({avgWindDir}°)</Text>
            ) : (
              <Text size="xs" c="dimmed">7-day avg</Text>
            )
          }
          color="gray"
        />
      </SimpleGrid>

      {/* Charts */}
      <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
        {/* Snow Depth Chart */}
        <Box
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Group justify="space-between" align="center" mb="sm">
            <Text size="sm" c="dimmed" fw={500}>
              Snow Depth (7 Day)
            </Text>
            <Group gap="xs">
              <Group gap={4}>
                <Box style={{ width: 16, height: 2, background: 'var(--mantine-color-cyan-5)' }} />
                <Text size="xs" c="dimmed">Weighted Avg</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 16, height: 1, borderTop: `1px dashed ${STATION_LINE_COLOR}` }} />
                <Text size="xs" c="dimmed">Stations</Text>
              </Group>
            </Group>
          </Group>
          {snowChartData.length > 0 ? (
            <>
              <CompositeChart
                h={140}
                data={snowChartData}
                dataKey="date"
                series={[...stationLineSeries, weightedAreaSeries]}
                curveType="monotone"
                withXAxis
                withYAxis={false}
                withDots={false}
                withTooltip
                tooltipProps={{
                  content: ({ payload }) => {
                    if (!payload || payload.length === 0) return null;
                    const item = payload[0]?.payload;
                    if (!item) return null;
                    return (
                      <Box
                        style={{
                          background: 'var(--mantine-color-dark-7)',
                          border: '1px solid var(--mantine-color-dark-4)',
                          borderRadius: 4,
                          padding: '8px 12px',
                        }}
                      >
                        <Text size="xs" fw={600} c="white" mb={4}>{item.date}</Text>
                        <Text size="xs" c="cyan" fw={500}>
                          Weighted Avg: {typeof item.weighted === 'number' ? item.weighted.toFixed(1) : '—'}"
                        </Text>
                        {stationTriplets.map((triplet) => {
                          const station = stationMap.get(triplet);
                          const value = item[triplet];
                          if (value === undefined || station === undefined) return null;
                          return (
                            <Text key={triplet} size="xs" c="dimmed">
                              {station.stationName} ({station.distanceMiles.toFixed(1)} mi): {typeof value === 'number' ? value.toFixed(1) : '—'}"
                            </Text>
                          );
                        })}
                      </Box>
                    );
                  },
                }}
                strokeWidth={1}
                gridProps={{ display: 'none' }}
                xAxisProps={{
                  tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 10 },
                  tickLine: false,
                  axisLine: false,
                }}
              />
              {/* Station legend */}
              <Group gap="md" mt="xs" justify="center">
                {stations.map((station) => (
                  <Group key={station.stationTriplet} gap={4}>
                    <Box 
                      style={{ 
                        width: 12, 
                        height: 1, 
                        background: STATION_LINE_COLOR,
                        borderTop: `1px dashed ${STATION_LINE_COLOR}`,
                      }} 
                    />
                    <Text size="xs" c="dimmed">
                      {station.stationName} ({station.distanceMiles.toFixed(1)}mi)
                    </Text>
                  </Group>
                ))}
              </Group>
            </>
          ) : (
            <Text c="dimmed" size="sm" ta="center" py="lg">
              No snow data available
            </Text>
          )}
        </Box>

        {/* Temperature Chart */}
        <Box
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Group justify="space-between" align="center" mb="sm">
            <Text size="sm" c="dimmed" fw={500}>
              Temperature Range (7 Day)
            </Text>
            <Text size="xs" c="dimmed">Weighted Avg</Text>
          </Group>
          {tempChartData.length > 0 ? (
            <AreaChart
              h={140}
              data={tempChartData}
              dataKey="date"
              series={[
                { name: 'max', color: 'red' },
                { name: 'min', color: 'blue' },
              ]}
              curveType="monotone"
              withXAxis
              withYAxis={false}
              withDots
              dotProps={{ r: 3 }}
              withTooltip
              tooltipProps={{
                content: ({ payload }) => {
                  if (!payload || payload.length === 0) return null;
                  const item = payload[0]?.payload;
                  if (!item) return null;
                  return (
                    <Box
                      style={{
                        background: 'var(--mantine-color-dark-7)',
                        border: '1px solid var(--mantine-color-dark-4)',
                        borderRadius: 4,
                        padding: '6px 10px',
                      }}
                    >
                      <Text size="xs" fw={600} c="white">{item.date}</Text>
                      <Text size="xs" c="red">High: {item.max.toFixed(0)}°F</Text>
                      <Text size="xs" c="blue">Low: {item.min.toFixed(0)}°F</Text>
                    </Box>
                  );
                },
              }}
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
              No temperature data available
            </Text>
          )}
        </Box>
      </SimpleGrid>
    </Card>
  );
}
