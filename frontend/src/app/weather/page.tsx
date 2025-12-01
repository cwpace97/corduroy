'use client';

import { useQuery } from '@apollo/client/react';
import {
  Container,
  Text,
  Title,
  Center,
  Loader,
  Alert,
  Stack,
  Group,
  SegmentedControl,
  Box,
} from '@mantine/core';
import { IconAlertCircle, IconSnowflake } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { GET_ALL_RESORT_WEATHER } from '@/graphql/queries';
import { WeatherCard, ResortWeatherData } from '@/components/WeatherCard/WeatherCard';

interface GetAllResortWeatherData {
  allResortWeather: ResortWeatherData[];
}

type SortOption = 'name' | 'snow' | 'conditions';

export default function WeatherPage() {
  const { loading, error, data } = useQuery<GetAllResortWeatherData>(GET_ALL_RESORT_WEATHER, {
    variables: { days: 7 },
  });
  const [sortBy, setSortBy] = useState<SortOption>('snow');

  const sortedWeather = useMemo(() => {
    if (!data?.allResortWeather) return [];
    
    const weatherData = [...data.allResortWeather];
    
    switch (sortBy) {
      case 'name':
        return weatherData.sort((a, b) => a.resortName.localeCompare(b.resortName));
      case 'snow':
        return weatherData.sort((a, b) => {
          const aSnow = a.trend.latestSnowDepthIn ?? 0;
          const bSnow = b.trend.latestSnowDepthIn ?? 0;
          return bSnow - aSnow;
        });
      case 'conditions':
        const conditionOrder = { excellent: 0, good: 1, fair: 2, poor: 3, unknown: 4 };
        return weatherData.sort((a, b) => {
          const aOrder = conditionOrder[a.trend.snowConditions as keyof typeof conditionOrder] ?? 4;
          const bOrder = conditionOrder[b.trend.snowConditions as keyof typeof conditionOrder] ?? 4;
          return aOrder - bOrder;
        });
      default:
        return weatherData;
    }
  }, [data?.allResortWeather, sortBy]);

  if (loading) {
    return (
      <Center h="calc(100vh - 120px)">
        <Stack align="center" gap="md">
          <Loader size="xl" color="cyan" />
          <Text c="white" size="lg">Loading weather data...</Text>
        </Stack>
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="calc(100vh - 120px)">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error loading weather data"
          color="red"
          variant="filled"
        >
          {error.message}
        </Alert>
      </Center>
    );
  }

  const hasData = sortedWeather.length > 0;

  return (
    <Container fluid px="xl" py="md">
      <Group justify="space-between" align="flex-start" mb="lg">
        <Box>
          <Group gap="sm" mb="xs">
            {/* <IconSnowflake size={28} style={{ color: 'var(--mantine-color-cyan-5)' }} /> */}
            <Title order={1} c="white">
              Weather Conditions
            </Title>
          </Group>
          <Text c="dimmed">
            7-day weather trends from nearby SNOTEL stations
          </Text>
        </Box>

        <SegmentedControl
          value={sortBy}
          onChange={(value) => setSortBy(value as SortOption)}
          data={[
            { label: 'Most Snow', value: 'snow' },
            { label: 'Best Conditions', value: 'conditions' },
            { label: 'A-Z', value: 'name' },
          ]}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
          }}
        />
      </Group>

      {!hasData ? (
        <Center mt="xl">
          <Stack align="center" gap="xs">
            <IconSnowflake size={48} style={{ color: 'var(--mantine-color-dark-3)' }} />
            <Text c="dimmed" size="xl">No weather data available</Text>
            <Text c="dimmed">Run the SNOTEL data collector to fetch weather data</Text>
          </Stack>
        </Center>
      ) : (
        <Stack gap="md">
          {sortedWeather.map((weather) => (
            <WeatherCard key={weather.resortName} weather={weather} />
          ))}
        </Stack>
      )}
    </Container>
  );
}

