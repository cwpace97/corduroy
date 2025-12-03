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

interface HistoricalWeatherData {
  date: string;
  tempMinF: number | null;
  tempMaxF: number | null;
  snowfallTotalIn: number | null;
}

interface ResortWeatherSummary {
  resortName: string;
  stations: StationInfo[];
  trend: WeatherTrend;
  dailyData: DailyData[];
  historicalWeather: HistoricalWeatherData[];
}

interface ForecastDataPoint {
  validTime: string;
  tempHighF: number | null;
  tempLowF: number | null;
  snowAmountIn: number | null;
}

interface ResortForecastSummary {
  resortName: string;
  forecasts: ForecastDataPoint[];
}

interface GetResortsData {
  resorts: Resort[];
  allResortWeather: ResortWeatherSummary[];
  allResortForecasts: ResortForecastSummary[];
}

type SortOption = 'name' | 'baseDepth' | 'recentSnow' | 'forecastSnow' | 'lifts' | 'runs';

export default function HomePage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);
  const [sortBy, setSortBy] = useState<SortOption>('forecastSnow');

  // Normalize a resort name by removing spaces and converting to lowercase
  // This allows matching "arapahoebasin" with "Arapahoe Basin"
  const normalizeResortName = (name: string): string => {
    return name.toLowerCase().replace(/[\s-]/g, '');
  };

  // Create a map of resort name to weather data for quick lookup
  const weatherByResort = useMemo(() => {
    const map = new Map<string, ResortWeatherSummary>();
    if (data?.allResortWeather) {
      for (const weather of data.allResortWeather) {
        const resortName = weather.resortName;
        // Store with multiple key variations for flexible matching
        map.set(resortName.toLowerCase(), weather);
        map.set(normalizeResortName(resortName), weather);
      }
    }
    return map;
  }, [data?.allResortWeather]);

  // Create a map of resort name to forecast data for quick lookup
  const forecastByResort = useMemo(() => {
    const map = new Map<string, ResortForecastSummary>();
    if (data?.allResortForecasts) {
      for (const forecast of data.allResortForecasts) {
        const resortName = forecast.resortName;
        map.set(resortName.toLowerCase(), forecast);
        map.set(normalizeResortName(resortName), forecast);
      }
    }
    return map;
  }, [data?.allResortForecasts]);

  const getWeatherData = (location: string): ResortWeatherSummary | null => {
    // Try exact match, lowercase, then normalized (no spaces)
    return weatherByResort.get(location) 
      || weatherByResort.get(location.toLowerCase()) 
      || weatherByResort.get(normalizeResortName(location)) 
      || null;
  };

  const getForecastData = (location: string): ResortForecastSummary | null => {
    return forecastByResort.get(location) 
      || forecastByResort.get(location.toLowerCase()) 
      || forecastByResort.get(normalizeResortName(location)) 
      || null;
  };

  // Sort resorts based on selected option
  const sortedResorts = useMemo(() => {
    if (!data?.resorts) return [];
    
    const resorts = [...data.resorts];
    
    // Helper to calculate 7-day forecast snow for a resort (inline to capture closure)
    const calcForecastSnow = (location: string): number => {
      const forecast = forecastByResort.get(location) 
        || forecastByResort.get(location.toLowerCase()) 
        || forecastByResort.get(normalizeResortName(location));
      if (!forecast?.forecasts) return 0;
      
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const sevenDaysFromNow = new Date(today);
      sevenDaysFromNow.setDate(today.getDate() + 7);
      
      return forecast.forecasts
        .filter(f => {
          const forecastDate = new Date(f.validTime.split('T')[0] + 'T00:00:00');
          return forecastDate >= today && forecastDate < sevenDaysFromNow;
        })
        .reduce((sum, f) => sum + (f.snowAmountIn ?? 0), 0);
    };

    // Helper to calculate 7-day historical snowfall for a resort (inline to capture closure)
    const calcHistoricalSnow = (location: string): number => {
      const weather = weatherByResort.get(location) 
        || weatherByResort.get(location.toLowerCase()) 
        || weatherByResort.get(normalizeResortName(location));
      if (!weather?.historicalWeather) return 0;
      
      return weather.historicalWeather
        .filter(h => h.snowfallTotalIn !== null && h.snowfallTotalIn > 0)
        .reduce((sum, h) => sum + (h.snowfallTotalIn ?? 0), 0);
    };
    
    switch (sortBy) {
      case 'name':
        return resorts.sort((a, b) => a.location.localeCompare(b.location));
      case 'baseDepth':
        return resorts.sort((a, b) => {
          const aWeather = weatherByResort.get(a.location) 
            || weatherByResort.get(a.location.toLowerCase()) 
            || weatherByResort.get(normalizeResortName(a.location));
          const bWeather = weatherByResort.get(b.location) 
            || weatherByResort.get(b.location.toLowerCase()) 
            || weatherByResort.get(normalizeResortName(b.location));
          const aDepth = aWeather?.trend.latestSnowDepthIn ?? 0;
          const bDepth = bWeather?.trend.latestSnowDepthIn ?? 0;
          return bDepth - aDepth;
        });
      case 'recentSnow':
        return resorts.sort((a, b) => {
          const aSnow = calcHistoricalSnow(a.location);
          const bSnow = calcHistoricalSnow(b.location);
          return bSnow - aSnow;
        });
      case 'forecastSnow':
        return resorts.sort((a, b) => {
          const aSnow = calcForecastSnow(a.location);
          const bSnow = calcForecastSnow(b.location);
          return bSnow - aSnow;
        });
      case 'lifts':
        return resorts.sort((a, b) => b.openLifts - a.openLifts);
      case 'runs':
        return resorts.sort((a, b) => b.openRuns - a.openRuns);
      default:
        return resorts;
    }
  }, [data?.resorts, sortBy, weatherByResort, forecastByResort]);

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
      <Stack gap="md" mb="lg">
        <Group justify="space-between" align="flex-start" wrap="wrap">
          <Box>
            <Title order={1} c="white" mb="xs">
              Resort Overview
            </Title>
            <Text c="dimmed">
              Current lift and run status across all Colorado resorts
            </Text>
          </Box>
        </Group>

        <Box style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
          <SegmentedControl
            value={sortBy}
            onChange={(value) => setSortBy(value as SortOption)}
            data={[
              { label: 'A-Z', value: 'name' },
              { label: 'Runs', value: 'runs' },
              { label: 'Lifts', value: 'lifts' },
              { label: 'Base Depth', value: 'baseDepth' },
              { label: 'Recent Snow', value: 'recentSnow' },
              { label: 'Forecasted Snow', value: 'forecastSnow' },
            ]}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              minWidth: 'fit-content',
            }}
          />
        </Box>
      </Stack>

      <Stack gap="sm">
        {sortedResorts.map((resort) => {
          const weatherData = getWeatherData(resort.location);
          const forecastData = getForecastData(resort.location);
          return (
            <ResortCard 
              key={resort.location} 
              resort={resort} 
              weatherTrend={weatherData?.trend ?? null}
              dailyData={weatherData?.dailyData}
              historicalWeather={weatherData?.historicalWeather}
              forecasts={forecastData?.forecasts}
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
