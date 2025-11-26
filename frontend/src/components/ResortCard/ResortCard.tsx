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
import { IconCloud } from '@tabler/icons-react';
import { MiniLineChart } from '@/components/MiniLineChart/MiniLineChart';
import { StatsRing } from '@/components/StatsRing/StatsRing';

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
}

export function ResortCard({ resort }: ResortCardProps) {
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
      <Group gap="md" wrap="nowrap" align="center">
        
        {/* 1. Resort Name */}
        <Box style={{ minWidth: 140 }}>
          <Title order={3} c="white" size="h4">
            {resort.location}
          </Title>
          <Text c="dimmed" size="xs">
            Updated: {resort.lastUpdated}
          </Text>
        </Box>

        <Divider orientation="vertical" color="dark.4" />

        {/* 2. Weather Placeholder */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minWidth: 140,
          }}
        >
          <Stack align="center" gap={4}>
            <IconCloud size={32} style={{ color: 'var(--mantine-color-dark-3)' }} />
            <Text c="dimmed" size="xs">
              Weather
            </Text>
          </Stack>
        </Box>

        <Divider orientation="vertical" color="dark.4" />

        {/* 3. Lifts Stats Ring */}
        <Box
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
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
        <Box style={{ flex: 1, minWidth: 120 }}>
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
        <Box style={{ flex: 1, minWidth: 120 }}>
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
    </Card>
  );
}
