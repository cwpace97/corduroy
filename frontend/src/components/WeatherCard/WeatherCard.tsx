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
import { CompositeChart } from '@mantine/charts';
import {
  IconSnowflake,
  IconTemperature,
  IconDroplet,
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

export interface ResortWeatherData {
  resortName: string;
  stations: StationInfo[];
  trend: WeatherTrend;
  dailyData: DailyWeatherData[];
  hourlyData: HourlyWeatherData[];
}

export interface WeatherCardProps {
  weather: ResortWeatherData;
  forecast?: ResortForecastData;
}

// Single gray color for all station dashed lines
const STATION_LINE_COLOR = '#6b7280';

// Helper function to determine condition from snowfall amount
const getSnowfallCondition = (snowfallInches: number): 'poor' | 'fair' | 'good' | 'great' | 'epic' => {
  if (snowfallInches < 3) return 'poor';
  if (snowfallInches >= 3 && snowfallInches < 7) return 'fair';
  if (snowfallInches >= 7 && snowfallInches < 12) return 'good';
  if (snowfallInches >= 12 && snowfallInches < 20) return 'great';
  return 'epic';
};

const getConditionColor = (condition: string): string => {
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
    case 'excellent':
      return '#14b8a6'; // teal
    default:
      return '#6b7280'; // gray
  }
};

const getConditionLabel = (condition: string): string => {
  switch (condition) {
    case 'epic':
      return 'Epic';
    case 'great':
      return 'Great';
    case 'good':
      return 'Good';
    case 'fair':
      return 'Fair';
    case 'poor':
      return 'Poor';
    case 'excellent':
      return 'Excellent';
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

const formatDate = (dateStr: string): string => {
  // Handle both ISO format and space-separated format
  const normalizedStr = dateStr.replace(' ', 'T');
  const date = new Date(normalizedStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const getDateKey = (dateStr: string): string => {
  // Extract YYYY-MM-DD from various date formats
  return dateStr.split('T')[0].split(' ')[0];
};

interface StatBlockProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  trend?: React.ReactNode;
  color?: string;
}

function StatBlock({ icon, label, value, trend, color = 'blue' }: StatBlockProps) {
  return (
    <Box
      style={{
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: 8,
        padding: '12px 16px',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Top row: Icon, Label, Trend */}
      <Group justify="space-between" align="center" mb="xs">
        <Group gap="xs" align="center">
          <ThemeIcon size={24} variant="light" color={color} radius="md">
            {icon}
          </ThemeIcon>
          <Text size="xs" c="dimmed" tt="uppercase" fw={500}>
            {label}
          </Text>
        </Group>
        {trend && (
          <Box>
            {trend}
          </Box>
        )}
      </Group>
      
      {/* Centered large value */}
      <Box style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Text size="2rem" fw={700} c="white" ta="center">
          {value}
        </Text>
      </Box>
    </Box>
  );
}

export function WeatherCard({ weather, forecast }: WeatherCardProps) {
  const { trend, dailyData, stations } = weather;
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

  // Process forecast data - group by date and merge high/low temps
  // NWS provides separate day/night periods, so we need to merge them
  const forecastByDate = new Map<string, ForecastDataPoint>();
  if (forecast?.forecasts) {
    // First pass: collect all forecasts by date, merging high/low from different periods
    const tempByDate = new Map<string, {
      high: number | null;
      low: number | null;
      snow: number | null;
      precip: number | null;
      precipProb: number | null;
      conditions: string | null;
      source: string;
      forecastTime: string;
      validTime: string;
    }>();
    
    forecast.forecasts.forEach(f => {
      const dateKey = f.validTime.split('T')[0].split(' ')[0];
      const existing = tempByDate.get(dateKey);
      
      if (!existing) {
        // First entry for this date
        tempByDate.set(dateKey, {
          high: f.tempHighF,
          low: f.tempLowF,
          snow: f.snowAmountIn,
          precip: f.precipAmountIn,
          precipProb: f.precipProbPct,
          conditions: f.conditionsText,
          source: f.source,
          forecastTime: f.forecastTime,
          validTime: f.validTime,
        });
      } else {
        // Merge with existing entry
        if (existing.high === null && f.tempHighF !== null) {
          existing.high = f.tempHighF;
        }
        if (existing.low === null && f.tempLowF !== null) {
          existing.low = f.tempLowF;
        }
        if (f.source === 'NWS' && f.snowAmountIn !== null) {
          existing.snow = f.snowAmountIn;
        } else if (existing.snow === null && f.snowAmountIn !== null) {
          existing.snow = f.snowAmountIn;
        }
        if (f.source === 'NWS' && f.conditionsText) {
          existing.conditions = f.conditionsText;
        } else if (!existing.conditions && f.conditionsText) {
          existing.conditions = f.conditionsText;
        }
        if (existing.precip === null && f.precipAmountIn !== null) {
          existing.precip = f.precipAmountIn;
        }
        if (existing.precipProb === null && f.precipProbPct !== null) {
          existing.precipProb = f.precipProbPct;
        }
      }
    });
    
    // Convert merged data back to ForecastDataPoint format
    tempByDate.forEach((data, dateKey) => {
      forecastByDate.set(dateKey, {
        source: data.source,
        forecastTime: data.forecastTime,
        validTime: data.validTime,
        tempHighF: data.high,
        tempLowF: data.low,
        snowAmountIn: data.snow,
        precipAmountIn: data.precip,
        precipProbPct: data.precipProb,
        windSpeedMph: null,
        windDirectionDeg: null,
        windGustMph: null,
        conditionsText: data.conditions,
        iconCode: null,
      });
    });
  }

  // Calculate historical snowfall from day-over-day snow depth changes
  const historicalSnowfall: Map<string, number> = new Map();
  const sortedDailyData = [...dailyData].sort((a, b) => a.date.localeCompare(b.date));
  for (let i = 1; i < sortedDailyData.length; i++) {
    const prevDepth = sortedDailyData[i - 1].snowDepthAvgIn;
    const currDepth = sortedDailyData[i].snowDepthAvgIn;
    if (prevDepth !== null && currDepth !== null) {
      const change = currDepth - prevDepth;
      // Only count positive changes as snowfall (negative is melting/settling)
      if (change > 0) {
        historicalSnowfall.set(getDateKey(sortedDailyData[i].date), change);
      }
    }
  }

  // Prepare HISTORICAL chart data
  const historicalChartData = dailyData
    .filter(d => d.tempMinF !== null || d.tempMaxF !== null)
    .map(d => {
      const dateKey = getDateKey(d.date);
      const snowfall = historicalSnowfall.get(dateKey) ?? 0;
      return {
        date: formatDate(d.date),
        fullDate: dateKey,
        min: d.tempMinF,
        max: d.tempMaxF,
        snowfall: snowfall > 0 ? snowfall : null,
      };
    });

  // Prepare FORECAST chart data
  const forecastChartData: Array<{
    date: string;
    fullDate: string;
    forecastMin: number | null;
    forecastMax: number | null;
    snowForecast: number | null;
    precipAmount: number | null;
    precipProb: number | null;
    conditions: string | null;
  }> = [];

  forecastByDate.forEach((forecastData, dateKey) => {
    forecastChartData.push({
      date: formatDate(dateKey),
      fullDate: dateKey,
      forecastMin: forecastData.tempLowF,
      forecastMax: forecastData.tempHighF,
      snowForecast: forecastData.snowAmountIn,
      precipAmount: forecastData.precipAmountIn,
      precipProb: forecastData.precipProbPct,
      conditions: forecastData.conditionsText,
    });
  });

  // Sort forecast data by date
  forecastChartData.sort((a, b) => a.fullDate.localeCompare(b.fullDate));

  // Fixed Y-axis domains for consistency across all charts
  const tempDomain: [number, number] = [-10, 40];  // Temperature: -10°F to 40°F
  const snowDomain: [number, number] = [0, 12];    // Snowfall: 0" to 12"

  // Calculate min/max temps for stats display
  const historicalTemps = dailyData.flatMap(d => [d.tempMinF, d.tempMaxF]).filter((t): t is number => t !== null);
  const minTemp = historicalTemps.length > 0 ? Math.min(...historicalTemps) : null;
  const maxTemp = historicalTemps.length > 0 ? Math.max(...historicalTemps) : null;

  // Calculate 7-day historical snowfall (from last 7 days of dailyData)
  const last7Days = sortedDailyData.slice(-7);
  const sevenDayHistoricalSnowfall = last7Days
    .map(d => historicalSnowfall.get(getDateKey(d.date)) ?? 0)
    .reduce((a, b) => a + b, 0);
  
  // Calculate 7-day forecast snow (next 7 days from today)
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const sevenDaysFromNow = new Date(today);
  sevenDaysFromNow.setDate(today.getDate() + 7);
  
  const sevenDayForecastSnow = Array.from(forecastByDate.entries())
    .filter(([dateKey]) => {
      const forecastDate = new Date(dateKey + 'T00:00:00');
      return forecastDate >= today && forecastDate < sevenDaysFromNow;
    })
    .map(([, f]) => f.snowAmountIn)
    .filter((s): s is number => s !== null)
    .reduce((a, b) => a + b, 0);

  // Calculate conditions based on 7-day totals
  const historical7Condition = getSnowfallCondition(sevenDayHistoricalSnowfall);
  const forecast7Condition = getSnowfallCondition(sevenDayForecastSnow);

  // Keep totalHistoricalSnowfall and totalForecastSnow for display in stats (all available data)
  const totalHistoricalSnowfall = Array.from(historicalSnowfall.values()).reduce((a, b) => a + b, 0);
  const totalForecastSnow = Array.from(forecastByDate.values())
    .map(f => f.snowAmountIn)
    .filter((s): s is number => s !== null)
    .reduce((a, b) => a + b, 0);

  // Get closest station for display
  const closestStation = stations[0];

  // Series for historical chart - temperature on left axis, snow on right axis
  const historicalSeries = [
    { name: 'max', color: 'red.5', type: 'line' as const, yAxisId: 'left' },
    { name: 'min', color: 'blue.5', type: 'line' as const, yAxisId: 'left' },
    { name: 'snowfall', color: 'cyan.4', type: 'bar' as const, yAxisId: 'right' },
  ];

  // Series for forecast chart - temperature on left axis, snow on right axis
  const forecastSeries = [
    { name: 'forecastMax', color: 'red.5', strokeDasharray: '6 4', type: 'line' as const, yAxisId: 'left' },
    { name: 'forecastMin', color: 'blue.5', strokeDasharray: '6 4', type: 'line' as const, yAxisId: 'left' },
    { name: 'snowForecast', color: 'cyan.4', type: 'bar' as const, yAxisId: 'right' },
  ];

  const hasForecastData = forecastChartData.length > 0;

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
        <Stack gap="xs" align="flex-end">
          <Group gap="sm" align="center">
            <Text size="sm" c="dimmed" fw={500}>
              Recent Snow
            </Text>
            <Badge
              size="lg"
              variant="filled"
              style={{
                backgroundColor: getConditionColor(historical7Condition),
                borderRadius: 20,
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title={`7d Historical: ${sevenDayHistoricalSnowfall.toFixed(1)}"`}
            >
              <Text size="sm" fw={600} c="white">
                {getConditionLabel(historical7Condition)}
              </Text>
            </Badge>
          </Group>
          <Group gap="sm" align="center">
            <Text size="sm" c="dimmed" fw={500}>
              Projected Snow
            </Text>
            <Badge
              size="lg"
              variant="filled"
              style={{
                backgroundColor: getConditionColor(forecast7Condition),
                borderRadius: 20,
                padding: '6px 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title={`7d Forecast: ${sevenDayForecastSnow.toFixed(1)}"`}
            >
              <Text size="sm" fw={600} c="white">
                {getConditionLabel(forecast7Condition)}
              </Text>
            </Badge>
          </Group>
        </Stack>
      </Group>

      <Divider color="dark.4" mb="md" />

      {/* ============ DESKTOP LAYOUT ============ */}
      
      {/* Row 1 Desktop: Snow Depth Chart (left) + Stats Boxes (right) */}
      <Group gap="md" align="stretch" mb="md" wrap="nowrap" style={{ minHeight: 140 }} className={styles.row1Desktop}>
        {/* Snow Depth Chart - Object A */}
        <Box
          style={{
            flex: '1 1 50%',
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Group justify="space-between" align="center" mb="xs">
            <Text size="sm" c="dimmed" fw={500}>
              Snow Depth (7d)
            </Text>
            <Group gap="md">
              <Group gap={4}>
                <Box style={{ width: 12, height: 2, background: 'var(--mantine-color-cyan-5)' }} />
                <Text size="xs" c="dimmed">Avg</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 12, height: 1, borderTop: `1px dashed ${STATION_LINE_COLOR}` }} />
                <Text size="xs" c="dimmed">Stations</Text>
              </Group>
            </Group>
          </Group>
          {snowChartData.length > 0 ? (
            <CompositeChart
              h={100}
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
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
              }}
            />
          ) : (
            <Text c="dimmed" size="sm" ta="center" py="lg">
              No snow data available
            </Text>
          )}
        </Box>

        {/* Stats Boxes - Object B (4 blocks) */}
        <Box style={{ flex: '1 1 50%' }}>
          <SimpleGrid cols={4} spacing="xs" style={{ height: '100%' }}>
            <StatBlock
              icon={<IconSnowflake size={14} />}
              label="Depth"
              value={trend.latestSnowDepthIn !== null ? `${trend.latestSnowDepthIn.toFixed(0)}"` : 'N/A'}
              color="cyan"
            />
            <StatBlock
              icon={<IconTemperature size={14} />}
              label="Temp"
              value={trend.tempAvgF !== null ? `${trend.tempAvgF.toFixed(0)}°` : 'N/A'}
              trend={
                minTemp !== null && maxTemp !== null ? (
                  <Text size="xs" c="dimmed">{minTemp.toFixed(0)}° / {maxTemp.toFixed(0)}°</Text>
                ) : undefined
              }
              color="orange"
            />
            <StatBlock
              icon={<IconDroplet size={14} />}
              label="7d Snow"
              value={totalHistoricalSnowfall > 0 ? `${totalHistoricalSnowfall.toFixed(1)}"` : '0"'}
              color="blue"
            />
            <StatBlock
              icon={<IconSnowflake size={14} />}
              label="Forecast"
              value={totalForecastSnow > 0 ? `${totalForecastSnow.toFixed(1)}"` : '0"'}
              trend={<Text size="xs" c="dimmed">7d</Text>}
              color="teal"
            />
          </SimpleGrid>
        </Box>
      </Group>

      {/* Row 2 Desktop: Historical and Forecast Temperature side by side */}
      <Group gap="md" align="stretch" grow preventGrowOverflow={false} wrap="nowrap" className={styles.row2Desktop}>
        {/* Historical Temperature Chart */}
        <Box
          style={{
            flex: hasForecastData ? '1 1 50%' : '1 1 100%',
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Group justify="space-between" align="center" mb="sm">
            <Text size="sm" c="dimmed" fw={500}>
              Historical (7d)
            </Text>
            <Group gap="md">
              <Group gap={4}>
                <Box style={{ width: 12, height: 2, background: 'var(--mantine-color-red-5)' }} />
                <Text size="xs" c="dimmed">High</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 12, height: 2, background: 'var(--mantine-color-blue-5)' }} />
                <Text size="xs" c="dimmed">Low</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 8, height: 8, background: 'var(--mantine-color-cyan-4)', borderRadius: 2 }} />
                <Text size="xs" c="dimmed">Snow</Text>
              </Group>
            </Group>
          </Group>
          {historicalChartData.length > 0 ? (
            <CompositeChart
              h={140}
              data={historicalChartData}
              dataKey="date"
              series={historicalSeries}
              curveType="monotone"
              withXAxis
              withYAxis
              withRightYAxis
              yAxisProps={{
                domain: tempDomain,
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}°`,
              }}
              rightYAxisProps={{
                domain: snowDomain,
                tick: { fill: 'var(--mantine-color-cyan-4)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}"`,
              }}
              withDots
              dotProps={{ r: 2 }}
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
                        borderRadius: 6,
                        padding: '10px 14px',
                        minWidth: 140,
                      }}
                    >
                      <Text size="sm" fw={600} c="white" mb={6}>{item.date}</Text>
                      <Group gap="md" mb={4}>
                        <Text size="xs" c="red.4">High: {item.max?.toFixed(0) ?? '—'}°F</Text>
                        <Text size="xs" c="blue.4">Low: {item.min?.toFixed(0) ?? '—'}°F</Text>
                      </Group>
                      {item.snowfall !== null && item.snowfall > 0 && (
                        <Text size="xs" c="cyan.4">
                          <IconSnowflake size={10} style={{ marginRight: 2, verticalAlign: 'middle' }} />
                          +{item.snowfall.toFixed(1)}" new snow
                        </Text>
                      )}
                    </Box>
                  );
                },
              }}
              strokeWidth={2}
              gridProps={{ display: 'none' }}
              xAxisProps={{
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
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

        {/* Forecast Temperature Chart */}
        {hasForecastData && (
          <Box
            style={{
              flex: '1 1 50%',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: 8,
              padding: 16,
              border: '1px solid rgba(255, 255, 255, 0.05)',
            }}
          >
            <Group justify="space-between" align="center" mb="sm">
              <Text size="sm" c="dimmed" fw={500}>
                Forecast (7d)
              </Text>
              <Group gap="md">
                <Group gap={4}>
                  <Box style={{ width: 12, height: 1, borderTop: '2px dashed var(--mantine-color-red-5)' }} />
                  <Text size="xs" c="dimmed">High</Text>
                </Group>
                <Group gap={4}>
                  <Box style={{ width: 12, height: 1, borderTop: '2px dashed var(--mantine-color-blue-5)' }} />
                  <Text size="xs" c="dimmed">Low</Text>
                </Group>
                <Group gap={4}>
                  <Box style={{ width: 8, height: 8, background: 'var(--mantine-color-cyan-4)', borderRadius: 2 }} />
                  <Text size="xs" c="dimmed">Snow</Text>
                </Group>
              </Group>
            </Group>
            <CompositeChart
              h={140}
              data={forecastChartData}
              dataKey="date"
              series={forecastSeries}
              curveType="monotone"
              withXAxis
              withYAxis
              withRightYAxis
              yAxisProps={{
                domain: tempDomain,
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}°`,
              }}
              rightYAxisProps={{
                domain: snowDomain,
                tick: { fill: 'var(--mantine-color-cyan-4)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}"`,
              }}
              withDots
              dotProps={{ r: 2 }}
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
                        borderRadius: 6,
                        padding: '10px 14px',
                        minWidth: 180,
                      }}
                    >
                      <Text size="sm" fw={600} c="white" mb={6}>{item.date}</Text>
                      
                      <Group gap="md" mb={4}>
                        <Text size="xs" c="red.4">High: {item.forecastMax?.toFixed(0) ?? '—'}°F</Text>
                        <Text size="xs" c="blue.4">Low: {item.forecastMin?.toFixed(0) ?? '—'}°F</Text>
                      </Group>
                      
                      {item.conditions && (
                        <Text size="xs" c="white" fw={500} mb={4}>
                          {item.conditions}
                        </Text>
                      )}
                      
                      <Group gap="md">
                        {item.snowForecast !== null && item.snowForecast > 0 && (
                          <Text size="xs" c="cyan.4">
                            <IconSnowflake size={10} style={{ marginRight: 2, verticalAlign: 'middle' }} />
                            {item.snowForecast.toFixed(1)}" snow
                          </Text>
                        )}
                        {item.precipAmount !== null && item.precipAmount > 0 && (
                          <Text size="xs" c="blue.3">
                            <IconDroplet size={10} style={{ marginRight: 2, verticalAlign: 'middle' }} />
                            {item.precipAmount.toFixed(2)}" precip
                          </Text>
                        )}
                        {item.precipProb !== null && (
                          <Text size="xs" c="gray.4">
                            {item.precipProb}% chance
                          </Text>
                        )}
                      </Group>
                    </Box>
                  );
                },
              }}
              strokeWidth={2}
              gridProps={{ display: 'none' }}
              xAxisProps={{
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
              }}
            />
          </Box>
        )}
      </Group>

      {/* ============ MOBILE LAYOUT ============ */}
      
      {/* Mobile: Stack all 4 sections vertically */}
      <Stack gap="md" className={styles.row1Mobile}>
        {/* 1. Snow Depth Chart */}
        <Box
          style={{
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 8,
            padding: 16,
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <Group justify="space-between" align="center" mb="xs">
            <Text size="sm" c="dimmed" fw={500}>
              Snow Depth (7d)
            </Text>
            <Group gap="md">
              <Group gap={4}>
                <Box style={{ width: 12, height: 2, background: 'var(--mantine-color-cyan-5)' }} />
                <Text size="xs" c="dimmed">Avg</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 12, height: 1, borderTop: `1px dashed ${STATION_LINE_COLOR}` }} />
                <Text size="xs" c="dimmed">Stations</Text>
              </Group>
            </Group>
          </Group>
          {snowChartData.length > 0 ? (
            <CompositeChart
              h={120}
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
                        Avg: {typeof item.weighted === 'number' ? item.weighted.toFixed(1) : '—'}"
                      </Text>
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
          ) : (
            <Text c="dimmed" size="sm" ta="center" py="lg">
              No snow data available
            </Text>
          )}
        </Box>

        {/* 2. Stats Boxes (4 blocks, 2x2 on mobile) */}
        <SimpleGrid cols={2} spacing="sm">
          <StatBlock
            icon={<IconSnowflake size={14} />}
            label="Depth"
            value={trend.latestSnowDepthIn !== null ? `${trend.latestSnowDepthIn.toFixed(0)}"` : 'N/A'}
            color="cyan"
          />
          <StatBlock
            icon={<IconTemperature size={14} />}
            label="Temp"
            value={trend.tempAvgF !== null ? `${trend.tempAvgF.toFixed(0)}°` : 'N/A'}
            trend={
              minTemp !== null && maxTemp !== null ? (
                <Text size="xs" c="dimmed">{minTemp.toFixed(0)}° / {maxTemp.toFixed(0)}°</Text>
              ) : undefined
            }
            color="orange"
          />
          <StatBlock
            icon={<IconDroplet size={14} />}
            label="7d Snow"
            value={totalHistoricalSnowfall > 0 ? `${totalHistoricalSnowfall.toFixed(1)}"` : '0"'}
            color="blue"
          />
          <StatBlock
            icon={<IconSnowflake size={14} />}
            label="Forecast"
            value={totalForecastSnow > 0 ? `${totalForecastSnow.toFixed(1)}"` : '0"'}
            trend={<Text size="xs" c="dimmed">7d</Text>}
            color="teal"
          />
        </SimpleGrid>

        {/* 3. Historical Temperature Chart */}
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
              Historical (7d)
            </Text>
            <Group gap="xs">
              <Group gap={4}>
                <Box style={{ width: 10, height: 2, background: 'var(--mantine-color-red-5)' }} />
                <Text size="xs" c="dimmed">H</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 10, height: 2, background: 'var(--mantine-color-blue-5)' }} />
                <Text size="xs" c="dimmed">L</Text>
              </Group>
              <Group gap={4}>
                <Box style={{ width: 6, height: 6, background: 'var(--mantine-color-cyan-4)', borderRadius: 1 }} />
                <Text size="xs" c="dimmed">❄</Text>
              </Group>
            </Group>
          </Group>
          {historicalChartData.length > 0 ? (
            <CompositeChart
              h={140}
              data={historicalChartData}
              dataKey="date"
              series={historicalSeries}
              curveType="monotone"
              withXAxis
              withYAxis
              withRightYAxis
              yAxisProps={{
                domain: tempDomain,
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}°`,
              }}
              rightYAxisProps={{
                domain: snowDomain,
                tick: { fill: 'var(--mantine-color-cyan-4)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}"`,
              }}
              withDots
              dotProps={{ r: 2 }}
              withTooltip
              strokeWidth={2}
              gridProps={{ display: 'none' }}
              xAxisProps={{
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
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

        {/* 4. Forecast Temperature Chart */}
        {hasForecastData && (
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
                Forecast (7d)
              </Text>
              <Group gap="xs">
                <Group gap={4}>
                  <Box style={{ width: 10, height: 1, borderTop: '2px dashed var(--mantine-color-red-5)' }} />
                  <Text size="xs" c="dimmed">H</Text>
                </Group>
                <Group gap={4}>
                  <Box style={{ width: 10, height: 1, borderTop: '2px dashed var(--mantine-color-blue-5)' }} />
                  <Text size="xs" c="dimmed">L</Text>
                </Group>
                <Group gap={4}>
                  <Box style={{ width: 6, height: 6, background: 'var(--mantine-color-cyan-4)', borderRadius: 1 }} />
                  <Text size="xs" c="dimmed">❄</Text>
                </Group>
              </Group>
            </Group>
            <CompositeChart
              h={140}
              data={forecastChartData}
              dataKey="date"
              series={forecastSeries}
              curveType="monotone"
              withXAxis
              withYAxis
              withRightYAxis
              yAxisProps={{
                domain: tempDomain,
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}°`,
              }}
              rightYAxisProps={{
                domain: snowDomain,
                tick: { fill: 'var(--mantine-color-cyan-4)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
                width: 28,
                tickFormatter: (value: number) => `${value}"`,
              }}
              withDots
              dotProps={{ r: 2 }}
              withTooltip
              strokeWidth={2}
              gridProps={{ display: 'none' }}
              xAxisProps={{
                tick: { fill: 'var(--mantine-color-dimmed)', fontSize: 9 },
                tickLine: false,
                axisLine: false,
              }}
            />
          </Box>
        )}
      </Stack>
    </Card>
  );
}
