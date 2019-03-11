#include "lest/lest.hpp"


const lest::test specification[] =
{
  CASE("I'm dumb")
  {
    EXPECT(true);
  }
};

int main( int argc, char * argv[] )
{
  return lest::run( specification, argc, argv );
}
