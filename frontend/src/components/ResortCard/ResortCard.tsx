'use client';

import {
  Card,
  Text,
  Title,
  Stack,
  Group,
  Divider,
  Box,
} from '@mantine/core';
import { MiniLineChart } from '@/components/MiniLineChart/MiniLineChart';
import { StatsRing } from '@/components/StatsRing/StatsRing';
import { WeatherSummary, WeatherTrend, DailyData, HistoricalWeatherData, ForecastDataPoint } from '@/components/WeatherSummary/WeatherSummary';
import styles from './ResortCard.module.css';

export interface Lift {
  liftName: string;
  liftType: string;
  liftStatus: string;
  dateOpened: string;
}

export interface Run {
  runName: string;
  runDifficulty: string;
  runStatus: string;
  dateOpened: string;
  runGroomed?: boolean;
}

export interface HistoryPoint {
  date: string;
  openCount: number;
}

export interface RecentlyOpenedItem {
  name: string;
  dateOpened: string;
}

export interface Resort {
  location: string;
  totalLifts: number;
  openLifts: number;
  totalRuns: number;
  openRuns: number;
  lastUpdated: string;
  lifts: Lift[];
  runs: Run[];
  liftsHistory: HistoryPoint[];
  runsHistory: HistoryPoint[];
  recentlyOpenedLifts: RecentlyOpenedItem[];
  recentlyOpenedRuns: RecentlyOpenedItem[];
}

export interface ResortCardProps {
  resort: Resort;
  weatherTrend?: WeatherTrend | null;
  dailyData?: DailyData[];
  historicalWeather?: HistoricalWeatherData[];
  forecasts?: ForecastDataPoint[];
}

export function ResortCard({ resort, weatherTrend, dailyData, historicalWeather, forecasts }: ResortCardProps) {
  return (
    <Card
      radius="md"
      p="sm"
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        overflow: 'hidden',
      }}
    >
      <Group gap="md" wrap="nowrap" align="center" className={styles.desktopLayout}>
        {/* 1. Resort Name */}
        <Box style={{ minWidth: 140, flex: '0 0 auto' }}>
          <Title order={3} c="white" size="h4">
            {resort.location}
          </Title>
          <Text c="dimmed" size="xs">
            Updated: {resort.lastUpdated}
          </Text>
        </Box>

        <Divider orientation="vertical" color="dark.4" />

        {/* 2. Weather Summary - wider box */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: 220,
            flex: '0 0 auto',
          }}
        >
          <WeatherSummary 
            trend={weatherTrend ?? null} 
            dailyData={dailyData} 
            historicalWeather={historicalWeather}
            forecasts={forecasts}
            compact 
          />
        </Box>

        <Divider orientation="vertical" color="dark.4" />

        {/* 3. Lifts Stats Ring */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flex: '0 0 auto',
          }}
        >
          <StatsRing
            label="Lifts"
            open={resort.openLifts}
            total={resort.totalLifts}
            color="teal"
          />
        </Box>

        {/* 4. Lifts History Chart */}
        <Box style={{ flex: '1 1 auto', minWidth: 100 }}>
          <Text c="dimmed" size="xs" mb={4}>
            Lifts 7-Day
          </Text>
          <MiniLineChart
            data={resort.liftsHistory}
            color="teal"
            maxValue={resort.totalLifts}
            totalCount={resort.totalLifts}
          />
        </Box>

        <Divider orientation="vertical" color="dark.4" />

        {/* 5. Runs Stats Ring */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flex: '0 0 auto',
          }}
        >
          <StatsRing
            label="Runs"
            open={resort.openRuns}
            total={resort.totalRuns}
            color="blue"
          />
        </Box>

        {/* 6. Runs History Chart */}
        <Box style={{ flex: '1 1 auto', minWidth: 100 }}>
          <Text c="dimmed" size="xs" mb={4}>
            Runs 7-Day
          </Text>
          <MiniLineChart
            data={resort.runsHistory}
            color="blue"
            maxValue={resort.totalRuns}
            totalCount={resort.totalRuns}
          />
        </Box>
      </Group>

      {/* Mobile Layout - only visible on small screens */}
      <Box className={styles.mobileLayout}>
        {/* Row 1: Name + Weather */}
        <Group gap="md" justify="space-between" align="center" className={styles.mobileRow}>
          <Box>
            <Title order={3} c="white" size="h4">
              {resort.location}
            </Title>
            <Text c="dimmed" size="xs">
              Updated: {resort.lastUpdated}
            </Text>
          </Box>
          <WeatherSummary 
            trend={weatherTrend ?? null} 
            dailyData={dailyData} 
            historicalWeather={historicalWeather}
            forecasts={forecasts}
            compact 
          />
        </Group>

        {/* Row 2: Lifts Stats + Chart */}
        <Group gap="md" wrap="nowrap" align="center" className={styles.mobileRow}>
          <Box style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <StatsRing
              label="Lifts"
              open={resort.openLifts}
              total={resort.totalLifts}
              color="teal"
            />
          </Box>
          <Box style={{ flex: 1 }}>
            <Text c="dimmed" size="xs" mb={4}>
              Lifts 7-Day
            </Text>
            <MiniLineChart
              data={resort.liftsHistory}
              color="teal"
              maxValue={resort.totalLifts}
              totalCount={resort.totalLifts}
            />
          </Box>
        </Group>

        {/* Row 3: Runs Stats + Chart */}
        <Group gap="md" wrap="nowrap" align="center" className={styles.mobileRow}>
          <Box style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <StatsRing
              label="Runs"
              open={resort.openRuns}
              total={resort.totalRuns}
              color="blue"
            />
          </Box>
          <Box style={{ flex: 1 }}>
            <Text c="dimmed" size="xs" mb={4}>
              Runs 7-Day
            </Text>
            <MiniLineChart
              data={resort.runsHistory}
              color="blue"
              maxValue={resort.totalRuns}
              totalCount={resort.totalRuns}
            />
          </Box>
        </Group>
      </Box>
    </Card>
  );
}
