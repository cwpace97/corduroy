'use client';

import { Paper, Title, Text, SimpleGrid, Stack, Group } from '@mantine/core';
import { IconMapPin } from '@tabler/icons-react';

export interface RecentlyOpenedItem {
  name: string;
  location: string;
  dateOpened: string;
  liftType?: string;
  liftCategory?: string;
  liftSize?: number;
}

export interface RecentlyOpenedData {
  lifts?: RecentlyOpenedItem[];
  runs?: RecentlyOpenedItem[];
}

export interface RecentlyOpenedProps {
  data: RecentlyOpenedData | null | undefined;
}

function isToday(dateString: string | null | undefined): boolean {
  if (!dateString) return false;
  const today = new Date().toISOString().split('T')[0];
  return dateString.startsWith(today);
}

export function RecentlyOpened({ data }: RecentlyOpenedProps) {
  if (!data || (!data.lifts?.length && !data.runs?.length)) {
    return null;
  }

  return (
    <Paper
      p="lg"
      mb="lg"
      radius="md"
      style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <Title order={2} c="white" mb="lg">
        Recently Opened
      </Title>

      {data.lifts && data.lifts.length > 0 && (
        <Stack gap="md" mb="lg">
          <Title order={4} c="dimmed">
            Lifts
          </Title>
          <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 5 }} spacing="md">
            {data.lifts.map((lift, index) => {
              const openedToday = isToday(lift.dateOpened);
              return (
                <Paper
                  key={index}
                  p="md"
                  radius="sm"
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    transition: 'background 150ms ease',
                  }}
                  className="hover-card"
                >
                  <Stack gap={4}>
                    <Text
                      c="white"
                      fw={600}
                      size="sm"
                      lineClamp={2}
                      title={lift.name}
                    >
                      {lift.name}
                    </Text>
                    <Group gap={4}>
                      <IconMapPin size={12} style={{ color: 'var(--mantine-color-dimmed)' }} />
                      <Text c="dimmed" size="xs">
                        {lift.location}
                      </Text>
                    </Group>
                    <Text
                      c={openedToday ? 'green' : 'dimmed'}
                      size="xs"
                      fw={500}
                    >
                      Opened: {lift.dateOpened}
                    </Text>
                  </Stack>
                </Paper>
              );
            })}
          </SimpleGrid>
        </Stack>
      )}

      {data.runs && data.runs.length > 0 && (
        <Stack gap="md">
          <Title order={4} c="dimmed">
            Runs
          </Title>
          <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 5 }} spacing="md">
            {data.runs.map((run, index) => {
              const openedToday = isToday(run.dateOpened);
              return (
                <Paper
                  key={index}
                  p="md"
                  radius="sm"
                  style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    transition: 'background 150ms ease',
                  }}
                  className="hover-card"
                >
                  <Stack gap={4}>
                    <Text
                      c="white"
                      fw={600}
                      size="sm"
                      lineClamp={2}
                      title={run.name}
                    >
                      {run.name}
                    </Text>
                    <Group gap={4}>
                      <IconMapPin size={12} style={{ color: 'var(--mantine-color-dimmed)' }} />
                      <Text c="dimmed" size="xs">
                        {run.location}
                      </Text>
                    </Group>
                    <Text
                      c={openedToday ? 'blue' : 'dimmed'}
                      size="xs"
                      fw={500}
                    >
                      Opened: {run.dateOpened}
                    </Text>
                  </Stack>
                </Paper>
              );
            })}
          </SimpleGrid>
        </Stack>
      )}
    </Paper>
  );
}

