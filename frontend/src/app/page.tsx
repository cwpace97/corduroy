'use client';

import { useQuery } from '@apollo/client/react';
import { useMemo, useState } from 'react';
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
import { IconAlertCircle } from '@tabler/icons-react';
import { GET_RESORTS } from '@/graphql/queries';
import { ResortCard, Resort } from '@/components/ResortCard/ResortCard';
import { WeatherTrend, DailyData } from '@/components/WeatherSummary/WeatherSummary';

interface StationInfo {
  stationName: string;
  stationTriplet: string;
  distanceMiles: number;
}

interface ResortWeatherSummary {
  resortName: string;
  stations: StationInfo[];
  trend: WeatherTrend;
  dailyData: DailyData[];
}

interface GetResortsData {
  resorts: Resort[];
  allResortWeather: ResortWeatherSummary[];
}

type SortOption = 'name' | 'snow' | 'conditions' | 'lifts' | 'runs';

export default function HomePage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);
  const [sortBy, setSortBy] = useState<SortOption>('conditions');

  // Create a map of resort name to weather data for quick lookup
  const weatherByResort = useMemo(() => {
    const map = new Map<string, ResortWeatherSummary>();
    if (data?.allResortWeather) {
      for (const weather of data.allResortWeather) {
        const resortName = weather.resortName;
        map.set(resortName.toLowerCase(), weather);
        if (resortName === 'Arapahoe Basin') {
          map.set('arapahoe basin', weather);
        }
      }
    }
    return map;
  }, [data?.allResortWeather]);

  const getWeatherData = (location: string): ResortWeatherSummary | null => {
    return weatherByResort.get(location) || weatherByResort.get(location.toLowerCase()) || null;
  };

  // Sort resorts based on selected option
  const sortedResorts = useMemo(() => {
    if (!data?.resorts) return [];
    
    const resorts = [...data.resorts];
    
    switch (sortBy) {
      case 'name':
        return resorts.sort((a, b) => a.location.localeCompare(b.location));
      case 'snow':
        return resorts.sort((a, b) => {
          const aWeather = getWeatherData(a.location);
          const bWeather = getWeatherData(b.location);
          const aSnow = aWeather?.trend.latestSnowDepthIn ?? 0;
          const bSnow = bWeather?.trend.latestSnowDepthIn ?? 0;
          return bSnow - aSnow;
        });
      case 'conditions':
        const conditionOrder = { excellent: 0, good: 1, fair: 2, poor: 3, unknown: 4 };
        return resorts.sort((a, b) => {
          const aWeather = getWeatherData(a.location);
          const bWeather = getWeatherData(b.location);
          const aOrder = conditionOrder[aWeather?.trend.snowConditions as keyof typeof conditionOrder] ?? 4;
          const bOrder = conditionOrder[bWeather?.trend.snowConditions as keyof typeof conditionOrder] ?? 4;
          return aOrder - bOrder;
        });
      case 'lifts':
        return resorts.sort((a, b) => b.openLifts - a.openLifts);
      case 'runs':
        return resorts.sort((a, b) => b.openRuns - a.openRuns);
      default:
        return resorts;
    }
  }, [data?.resorts, sortBy, weatherByResort]);

  if (loading) {
    return (
      <Center h="calc(100vh - 120px)">
        <Stack align="center" gap="md">
          <Loader size="xl" color="blue" />
          <Text c="white" size="lg">Loading resort data...</Text>
        </Stack>
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="calc(100vh - 120px)">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error loading resort data"
          color="red"
          variant="filled"
        >
          {error.message}
        </Alert>
      </Center>
    );
  }

  return (
    <Container fluid px="xl" py="md">
      <Group justify="space-between" align="flex-start" mb="lg">
        <Box>
          <Title order={1} c="white" mb="xs">
            Resort Overview
          </Title>
          <Text c="dimmed">
            Current lift and run status across all Colorado resorts
          </Text>
        </Box>

        <SegmentedControl
          value={sortBy}
          onChange={(value) => setSortBy(value as SortOption)}
          data={[
            { label: 'A-Z', value: 'name' },
            { label: 'Total Runs Open', value: 'runs' },
            { label: 'Total Lifts Open', value: 'lifts' },
            { label: 'Total Snow Depth', value: 'snow' },
            { label: 'Best Conditions', value: 'conditions' },
          ]}
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
          }}
        />
      </Group>

      <Stack gap="sm">
        {sortedResorts.map((resort) => {
          const weatherData = getWeatherData(resort.location);
          return (
            <ResortCard 
              key={resort.location} 
              resort={resort} 
              weatherTrend={weatherData?.trend ?? null}
              dailyData={weatherData?.dailyData}
            />
          );
        })}
      </Stack>

      {(!data?.resorts || data.resorts.length === 0) && (
        <Center mt="xl">
          <Stack align="center" gap="xs">
            <Text c="dimmed" size="xl">No resort data available</Text>
            <Text c="dimmed">Run the scrapers to collect data</Text>
          </Stack>
        </Center>
      )}
    </Container>
  );
}
