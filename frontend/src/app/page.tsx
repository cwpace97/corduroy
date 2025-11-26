'use client';

import { useQuery } from '@apollo/client/react';
import {
  Container,
  Text,
  Center,
  Loader,
  Alert,
  Stack,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { GET_RESORTS } from '@/graphql/queries';
import { ResortCard, Resort } from '@/components/ResortCard/ResortCard';

interface GetResortsData {
  resorts: Resort[];
}

export default function HomePage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);

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
      <Stack gap="sm">
        {data?.resorts?.map((resort) => (
          <ResortCard key={resort.location} resort={resort} />
        ))}
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
