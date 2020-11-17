/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "mcModule.hpp"

SC_IMPLEMENT_MODULE(MicroClimateChartModule)

sc_result MicroClimateChartModule::InitializeImpl()
{
  m_mcService.reset(new MicroClimateChartPythonService("MicroClimateChartScript/DrawChart.py"));
  m_mcService->Run();
  return SC_RESULT_OK;
}

sc_result MicroClimateChartModule::ShutdownImpl()
{
  m_mcService->Stop();
  m_mcService.reset();
  return SC_RESULT_OK;
}
