'use client';

import { Center, RingProgress, Text, Stack } from '@mantine/core';

interface StatsRingProps {
  label: string;
  open: number;
  total: number;
  color: string;
}

export function StatsRing({ label, open, total, color }: StatsRingProps) {
  const percentage = total > 0 ? Math.round((open / total) * 100) : 0;

  return (
    <Stack align="center" gap={4}>
      <Text c="dimmed" size="xs" fw={600} tt="uppercase">
        {label}
      </Text>
      <RingProgress
        size={100}
        roundCaps
        thickness={10}
        sections={[{ value: percentage, color }]}
        label={
          <Center>
            <Stack align="center" gap={0}>
              <Text fw={700} size="lg" c="white">
                {open}
              </Text>
              <Text size="xs" c="dimmed">
                / {total}
              </Text>
            </Stack>
          </Center>
        }
      />
      <Text size="sm" c="dimmed">
        {percentage}%
      </Text>
    </Stack>
  );
}

