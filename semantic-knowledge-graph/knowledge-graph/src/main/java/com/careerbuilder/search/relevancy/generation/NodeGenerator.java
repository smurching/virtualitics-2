package com.careerbuilder.search.relevancy.generation;

import com.careerbuilder.search.relevancy.model.RequestNode;
import com.careerbuilder.search.relevancy.model.ResponseNode;
import com.careerbuilder.search.relevancy.model.ResponseValue;
import com.careerbuilder.search.relevancy.NodeContext;
import com.careerbuilder.search.relevancy.RecursionOp;
import com.careerbuilder.search.relevancy.waitable.AggregationWaitable;
import com.careerbuilder.search.relevancy.waitable.Waitable;
import com.careerbuilder.search.relevancy.threadpool.ThreadPool;
import org.apache.lucene.search.MatchAllDocsQuery;
import org.apache.lucene.search.Sort;
import org.apache.solr.common.util.SimpleOrderedMap;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.Future;

public class NodeGenerator implements RecursionOp {

    public ResponseNode [] transform(NodeContext context, RequestNode [] requests, ResponseNode [] responses) throws IOException {
        ResponseNode [] resps = new ResponseNode[requests.length];
        AggregationWaitable[] runners = buildWaitables(context, requests);
        List<Future<Waitable>> futures = ThreadPool.multiplex(runners);
        ThreadPool.demultiplex(futures);
        for(int i = 0; i < resps.length; ++i) {
            resps[i] = new ResponseNode(requests[i].type);
            mergeResponseValues(requests[i], resps[i], runners[i]);
        }
        return resps;
    }

    private void mergeResponseValues(RequestNode request, ResponseNode resp, AggregationWaitable runner) {
        int genLength = runner == null ? 0 : runner.buckets == null ? 0 :runner.buckets.size();
        int requestValsLength = request.values == null ? 0 : request.values.length;
        resp.values = new ResponseValue[requestValsLength + genLength];
        int k = addPassedInValues(request, resp);
        if(runner != null) {
            addGeneratedValues(resp, runner, k);
        }
    }

    private int addPassedInValues(RequestNode request, ResponseNode resp) {
        int k = 0;
        if(request.values != null) {
            for (; k < request.values.length; ++k) {
                resp.values[k] = new ResponseValue(request.values[k]);
                resp.values[k].normalizedValue = request.normalizedValues == null ? null : request.normalizedValues.get(k);
            }
        }
        return k;
    }

    private void addGeneratedValues(ResponseNode resp, AggregationWaitable runner, int k) {
        for (SimpleOrderedMap<Object> bucket: runner.buckets) {
            ResponseValue respValue = new ResponseValue(runner.adapter.getStringValue(bucket));
            respValue.normalizedValue = runner.adapter.getMapValue(bucket);
            resp.values[k++] = respValue;
        }
    }

    private AggregationWaitable[] buildWaitables(NodeContext context,
                                               RequestNode [] requests) throws IOException {
        AggregationWaitable[] runners = new AggregationWaitable[requests.length];
        for(int i = 0; i < requests.length; ++i) {
            if(requests[i].discover_values) {
                // populate required docListAndSet once and only if necessary
                if(context.queryDomainList == null) {
                   context.queryDomainList =
                           context.req.getSearcher().getDocListAndSet(new MatchAllDocsQuery(),
                                   context.queryDomain, Sort.INDEXORDER, 0, 0);
                }
                FacetFieldAdapter adapter = new FacetFieldAdapter(context, requests[i].type);
                runners[i] = new AggregationWaitable(context,
                        adapter,
                        adapter.field,
                        0,
                        requests[i].limit);
            }
        }
        return runners;
    }
}
