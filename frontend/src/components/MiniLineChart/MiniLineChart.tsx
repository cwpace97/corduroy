'use client';

import { AreaChart } from '@mantine/charts';
import { Text, Stack, Group } from '@mantine/core';

interface HistoryPoint {
  date: string;
  openCount: number;
}

interface MiniLineChartProps {
  data: HistoryPoint[] | null | undefined;
  color?: string;
  maxValue?: number | null;
  totalCount?: number | null;
}

export function MiniLineChart({ 
  data, 
  color = 'teal', 
  totalCount 
}: MiniLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <Text c="dimmed" size="xs" ta="center" py="md">
        No history data
      </Text>
    );
  }

  // Transform data for Mantine charts
  const chartData = data.map((point) => ({
    date: point.date,
    open: point.openCount,
  }));

  return (
    <Stack gap={4}>
      <AreaChart
        h={60}
        data={chartData}
        dataKey="date"
        series={[{ name: 'open', color }]}
        curveType="linear"
        withXAxis={false}
        withYAxis={false}
        withDots={true}
        dotProps={{ r: 3 }}
        withTooltip
        tooltipProps={{
          content: ({ payload }) => {
            if (!payload || payload.length === 0) return null;
            const item = payload[0]?.payload;
            if (!item) return null;
            return (
              <div style={{
                background: 'var(--mantine-color-dark-7)',
                border: '1px solid var(--mantine-color-dark-4)',
                borderRadius: 4,
                padding: '6px 10px',
              }}>
                <Text size="xs" fw={600} c="white">{item.date}</Text>
                <Text size="xs" c="dimmed">{item.open} open</Text>
                {totalCount && (
                  <Text size="xs" c="dimmed">
                    {Math.round((item.open / totalCount) * 100)}%
                  </Text>
                )}
              </div>
            );
          },
        }}
        fillOpacity={0.3}
        strokeWidth={2}
        gridProps={{ display: 'none' }}
      />
      <Group justify="space-between" px={2}>
        <Text size="xs" c="dimmed">{data[0]?.date}</Text>
        <Text size="xs" c="dimmed">{data[data.length - 1]?.date}</Text>
      </Group>
    </Stack>
  );
}

