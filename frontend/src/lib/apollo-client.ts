import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client/core';

const httpLink = new HttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql',
});

export function makeClient() {
  return new ApolloClient({
    link: httpLink,
    cache: new InMemoryCache(),
  });
}
