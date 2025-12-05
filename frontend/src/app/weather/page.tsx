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
  Chip,
  Box,
} from '@mantine/core';
import { IconAlertCircle, IconSnowflake } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { GET_ALL_RESORT_WEATHER, GET_ALL_RESORT_FORECASTS } from '@/graphql/queries';
import { WeatherCard, ResortWeatherData, ResortForecastData } from '@/components/WeatherCard/WeatherCard';
import { PASS_OPTIONS, getResortPass } from '@/lib/constants';

interface GetAllResortWeatherData {
  allResortWeather: ResortWeatherData[];
}

interface GetAllResortForecastsData {
  allResortForecasts: ResortForecastData[];
}

type SortOption = 'name' | 'depth' | 'recent' | 'forecast';

// Helper to calculate recent snowfall from historical weather data (Open-Meteo snowfall totals)
const calculateRecentSnowfall = (weather: ResortWeatherData): number => {
  if (!weather.historicalWeather) return 0;
  
  return weather.historicalWeather
    .filter(h => h.snowfallTotalIn !== null && h.snowfallTotalIn > 0)
    .reduce((sum, h) => sum + (h.snowfallTotalIn ?? 0), 0);
};

// Helper to calculate forecast snow total
const calculateForecastSnow = (forecast: ResortForecastData | undefined): number => {
  if (!forecast?.forecasts) return 0;
  
  // Group by date and sum snow amounts
  const snowByDate = new Map<string, number>();
  forecast.forecasts.forEach(f => {
    if (f.snowAmountIn !== null && f.snowAmountIn > 0) {
      const dateKey = f.validTime.split('T')[0].split(' ')[0];
      const existing = snowByDate.get(dateKey) || 0;
      // Take the max for each date (in case of multiple sources)
      snowByDate.set(dateKey, Math.max(existing, f.snowAmountIn));
    }
  });
  
  return Array.from(snowByDate.values()).reduce((a, b) => a + b, 0);
};

export default function WeatherPage() {
  const { loading, error, data } = useQuery<GetAllResortWeatherData>(GET_ALL_RESORT_WEATHER, {
    variables: { days: 7 },
  });
  const { loading: forecastsLoading, error: forecastsError, data: forecastsData } = useQuery<GetAllResortForecastsData>(
    GET_ALL_RESORT_FORECASTS,
    {
      variables: { days: 7 },
    }
  );
  const [sortBy, setSortBy] = useState<SortOption>('forecast');
  const [selectedPass, setSelectedPass] = useState<string>('all');

  // Create a map of resort name to forecast data for easy lookup
  const forecastMap = useMemo(() => {
    const map = new Map<string, ResortForecastData>();
    forecastsData?.allResortForecasts?.forEach(forecast => {
      map.set(forecast.resortName, forecast);
    });
    return map;
  }, [forecastsData?.allResortForecasts]);

  const sortedWeather = useMemo(() => {
    if (!data?.allResortWeather) return [];
    
    // First filter by pass
    let weatherData = [...data.allResortWeather];
    if (selectedPass !== 'all') {
      weatherData = weatherData.filter(weather => {
        const pass = getResortPass(weather.resortName);
        return pass === selectedPass;
      });
    }
    
    switch (sortBy) {
      case 'name':
        return weatherData.sort((a, b) => a.resortName.localeCompare(b.resortName));
      case 'depth':
        return weatherData.sort((a, b) => {
          const aSnow = a.trend.latestSnowDepthIn ?? 0;
          const bSnow = b.trend.latestSnowDepthIn ?? 0;
          return bSnow - aSnow;
        });
      case 'recent':
        return weatherData.sort((a, b) => {
          const aRecent = calculateRecentSnowfall(a);
          const bRecent = calculateRecentSnowfall(b);
          return bRecent - aRecent;
        });
      case 'forecast':
        return weatherData.sort((a, b) => {
          const aForecast = calculateForecastSnow(forecastMap.get(a.resortName));
          const bForecast = calculateForecastSnow(forecastMap.get(b.resortName));
          return bForecast - aForecast;
        });
      default:
        return weatherData;
    }
  }, [data?.allResortWeather, sortBy, selectedPass, forecastMap]);

  if (loading || forecastsLoading) {
    return (
      <Center h="calc(100vh - 120px)">
        <Stack align="center" gap="md">
          <Loader size="xl" color="cyan" />
          <Text c="white" size="lg">Loading weather data...</Text>
        </Stack>
      </Center>
    );
  }

  if (error || forecastsError) {
    return (
      <Center h="calc(100vh - 120px)">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error loading weather data"
          color="red"
          variant="filled"
        >
          {error?.message || forecastsError?.message || 'Unknown error'}
        </Alert>
      </Center>
    );
  }

  const hasData = sortedWeather.length > 0;

  return (
    <Container fluid px={{ base: 8, sm: 32 }} py="md">
      <Stack gap="md" mb="lg">
        <Group justify="space-between" align="flex-start" wrap="wrap">
          <Box>
            <Title order={1} c="white" mb="xs">
              Weather Conditions
            </Title>
            <Text c="dimmed">
              7-day historical + 7-day forecast from SNOTEL & weather services
            </Text>
          </Box>
        </Group>

        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Pass
          </Text>
          <Chip.Group value={selectedPass} onChange={(value) => setSelectedPass(value as string)}>
            <Group gap="xs">
              {PASS_OPTIONS.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm">
                  {option.label}
                </Chip>
              ))}
            </Group>
          </Chip.Group>
        </Box>

        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Sort by
          </Text>
          <Chip.Group value={sortBy} onChange={(value) => setSortBy(value as SortOption)}>
            <Group gap="xs">
              <Chip value="name" variant="outline" radius="sm">A-Z</Chip>
              <Chip value="depth" variant="outline" radius="sm">Snow Depth</Chip>
              <Chip value="recent" variant="outline" radius="sm">Recent Snow</Chip>
              <Chip value="forecast" variant="outline" radius="sm">Forecast Snow</Chip>
            </Group>
          </Chip.Group>
        </Box>
      </Stack>

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
            <WeatherCard 
              key={weather.resortName} 
              weather={weather} 
              forecast={forecastMap.get(weather.resortName)}
            />
          ))}
        </Stack>
      )}
    </Container>
  );
}

